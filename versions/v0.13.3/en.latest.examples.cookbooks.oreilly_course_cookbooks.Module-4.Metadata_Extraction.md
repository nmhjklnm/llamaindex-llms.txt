# Metadata Extraction¶
In this notebook we will demonstrate following:
  1. RAG using Metadata Extractors.
  2. Extract Metadata using PydanticProgram.


## Installation¶
In [ ]:
Copied!
```
!pip install llama-index
!pip install llama_index-readers-web

```

!pip install llama-index !pip install llama_index-readers-web
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

import os

```

import nest_asyncio nest_asyncio.apply() import os
## Setup API Key¶
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "sk-..."

```

os.environ["OPENAI_API_KEY"] = "sk-..."
## Define LLM¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import MetadataMode
from llama_index.core import Settings

```

from llama_index.llms.openai import OpenAI from llama_index.core.schema import MetadataMode from llama_index.core import Settings
In [ ]:
Copied!
```
llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", max_tokens=512)
Settings.llm = llm

```

llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", max_tokens=512) Settings.llm = llm
## Node Parser and Metadata Extractors¶
In [ ]:
Copied!
```
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    QuestionsAnsweredExtractor,
)

node_parser = TokenTextSplitter(
    separator=" ", chunk_size=256, chunk_overlap=128
)

question_extractor = QuestionsAnsweredExtractor(
    questions=3, llm=llm, metadata_mode=MetadataMode.EMBED
)

```

from llama_index.core.node_parser import TokenTextSplitter from llama_index.core.extractors import ( QuestionsAnsweredExtractor, ) node_parser = TokenTextSplitter( separator=" ", chunk_size=256, chunk_overlap=128 ) question_extractor = QuestionsAnsweredExtractor( questions=3, llm=llm, metadata_mode=MetadataMode.EMBED )
## Load Data¶
In [ ]:
Copied!
```
from llama_index.readers.web import SimpleWebPageReader

reader = SimpleWebPageReader(html_to_text=True)
docs = reader.load_data(urls=["https://eugeneyan.com/writing/llm-patterns/"])

```

from llama_index.readers.web import SimpleWebPageReader reader = SimpleWebPageReader(html_to_text=True) docs = reader.load_data(urls=["https://eugeneyan.com/writing/llm-patterns/"])
In [ ]:
Copied!
```
print(docs[0].get_content())

```

print(docs[0].get_content())
```
# [eugeneyan](/)

  * [Start Here](/start-here/ "Start Here")
  * [Writing](/writing/ "Writing")
  * [Speaking](/speaking/ "Speaking")
  * [Prototyping](/prototyping/ "Prototyping")
  * [About](/about/ "About")

# Patterns for Building LLM-based Systems & Products

[ [llm](/tag/llm/) [engineering](/tag/engineering/)
[production](/tag/production/) [🔥](/tag/🔥/) ]  · 66 min read

> Discussions on [HackerNews](https://news.ycombinator.com/item?id=36965993),
> [Twitter](https://twitter.com/eugeneyan/status/1686531758701899776), and
> [LinkedIn](https://www.linkedin.com/posts/eugeneyan_patterns-for-building-
> llm-based-systems-activity-7092300473981927424-_wVo)

“There is a large class of problems that are easy to imagine and build demos
for, but extremely hard to make products out of. For example, self-driving:
It’s easy to demo a car self-driving around a block, but making it into a
product takes a decade.” -
[Karpathy](https://twitter.com/eugeneyan/status/1672692174704766976)

This write-up is about practical patterns for integrating large language
models (LLMs) into systems & products. We’ll build on academic research,
industry resources, and practitioner know-how, and distill them into key ideas
and practices.

There are seven key patterns. They’re also organized along the spectrum of
improving performance vs. reducing cost/risk, and closer to the data vs.
closer to the user.

  * Evals: To measure performance
  * RAG: To add recent, external knowledge
  * Fine-tuning: To get better at specific tasks
  * Caching: To reduce latency & cost
  * Guardrails: To ensure output quality
  * Defensive UX: To anticipate & manage errors gracefully
  * Collect user feedback: To build our data flywheel

(Also see this addendum on [how to match these LLM patterns to potential
problems](/writing/llm-problems/).)

![Image](/assets/llm-patterns-og.png)

LLM patterns: From data to user, from defensive to offensive (see connections
between patterns)

## Evals: To measure performance

Evaluations are a set of measurements used to assess a model’s performance on
a task. They include benchmark data and metrics. From a [HackerNews
comment](https://news.ycombinator.com/item?id=36789901):

> How important evals are to the team is a major differentiator between folks
> rushing out hot garbage and those seriously building products in the space.

### Why evals?

Evals enable us to measure how well our system or product is doing and detect
any regressions. (A system or product can be made up of multiple components
such as LLMs, prompt templates, retrieved context, and parameters like
temperature.) A representative set of evals takes us a step towards measuring
system changes at scale. Without evals, we would be flying blind, or would
have to visually inspect LLM outputs with each change.

### More about evals

**There are many benchmarks in the field of language modeling**. Some notable
ones are:

  * **[MMLU](https://arxiv.org/abs/2009.03300)** : A set of 57 tasks that span elementary math, US history, computer science, law, and more. To perform well, models must possess extensive world knowledge and problem-solving ability.
  * **[EleutherAI Eval](https://github.com/EleutherAI/lm-evaluation-harness)** : Unified framework to test models via zero/few-shot settings on 200 tasks. Incorporates a large number of evals including BigBench, MMLU, etc.
  * **[HELM](https://arxiv.org/abs/2211.09110)** : Instead of specific tasks and metrics, HELM offers a comprehensive assessment of LLMs by evaluating them across domains. Metrics include accuracy, calibration, robustness, fairness, bias, toxicity, etc. Tasks include Q&A, information retrieval, summarization, text classification, etc.
  * **[AlpacaEval](https://github.com/tatsu-lab/alpaca_eval)** : Automated evaluation framework which measures how often a strong LLM (e.g., GPT-4) prefers the output of one model over a reference model. Metrics include win rate, bias, latency, price, variance, etc. Validated to have high agreement with 20k human annotations.

We can group metrics into two categories: context-dependent or context-free.

  * **Context-dependent** : These take context into account. They’re often proposed for a specific task; repurposing them for other tasks will require some adjustment.
  * **Context-free** : These aren’t tied to the context when evaluating generated output; they only compare the output with the provided gold references. As they’re task agnostic, they’re easier to apply to a wide variety of tasks.

To get a better sense of these metrics (and their potential shortfalls), we’ll
explore a few of the commonly used metrics such as BLEU, ROUGE, BERTScore, and
MoverScore.

**[BLEU](https://dl.acm.org/doi/10.3115/1073083.1073135) (Bilingual Evaluation
Understudy)** is a precision-based metric: It counts the number of n-grams in
the generated output that also show up in the reference, and then divides it
by the total number of words in the output. It’s predominantly used in machine
translation and remains a popular metric due to its cost-effectiveness.

First, precision for various values of \\(n\\) is computed:

\\[\text{precision}_n = \frac{\sum_{p \in \text{output}} \sum_{\text{n-gram}
\in p} \text{Count}_{\text{clip}} (\text{n-gram})}{\sum_{p \in \text{output}}
\sum_{\text{n-gram} \in p} \text{Count}(\text{n-gram})}\\]

\\(Count_{clip}(\text{n-gram})\\) is clipped by the maximum number of times an
n-gram appears in any corresponding reference sentence.

\\[\text{Count}_{\text{clip}}(n\text{-gram}) = \min \left(\text{matched }
n\text{-gram count}, \max_{r \in R} \left(n\text{-gram count in }
r\right)\right)\\]

Once we’ve computed precision at various \\(n\\), a final BLEU-N score is
computed as the geometric mean of all the \\(precision_n\\) scores.

However, since precision relies solely on n-grams and doesn’t consider the
length of the generated output, an output containing just one unigram of a
common word (like a stop word) would achieve perfect precision. This can be
misleading and encourage outputs that contain fewer words to increase BLEU
scores. To counter this, a brevity penalty is added to penalize excessively
short sentences.

\\[BP = \begin{cases} 1 & \text{if } |p| > |r| \\\ e^{1-\frac{|r|}{|p|}} &
\text{otherwise} \end{cases}\\]

Thus, the final formula is:

\\[\text{BLEU-N} = BP \cdot \exp\left(\sum_{n=1}^{N} W_n
\log(\text{precision}_n)\right)\\]

**[ROUGE](https://aclanthology.org/W04-1013/) (Recall-Oriented Understudy for
Gisting Evaluation)**: In contrast to BLEU, ROUGE is recall-oriented. It
counts the number of words in the reference that also occur in the output.
It’s typically used to assess automatic summarization tasks.

There are several ROUGE variants. ROUGE-N is most similar to BLEU in that it
also counts the number of matching n-grams between the output and the
reference.

\\[\text{ROUGE-N} = \frac{\sum_{s_r \in \text{references}} \sum_{n\text{-gram}
\in s_r} \text{Count}_{\text{match}} (n\text{-gram})}{\sum_{s_r \in
\text{references}} \sum_{n\text{-gram} \in s_r} \text{Count}
(n\text{-gram})}\\]

Other variants include:

  * ROUGE-L: This measures the longest common subsequence (LCS) between the output and the reference. It considers sentence-level structure similarity and zeros in on the longest series of co-occurring in-sequence n-grams.
  * ROUGE-S: This measures the skip-bigram between the output and reference. Skip-bigrams are pairs of words that maintain their sentence order regardless of the words that might be sandwiched between them.

**[BERTScore](https://arxiv.org/abs/1904.09675)** is an embedding-based metric
that uses cosine similarity to compare each token or n-gram in the generated
output with the reference sentence. There are three components to BERTScore:

  * Recall: Average cosine similarity between each token in the reference and its closest match in the generated output.
  * Precision: Average cosine similarity between each token in the generated output and its nearest match in the reference.
  * F1: Harmonic mean of recall and precision

\\[Recall_{\text{BERT}} = \frac{1}{|r|} \sum_{i \in r} \max_{j \in p}
\vec{i}^T \vec{j}, \quad Precision_{\text{BERT}} = \frac{1}{|p|} \sum_{j \in
p} \max_{i \in r} \vec{i}^T \vec{j}\\] \\[\text{BERTscore} = F_{\text{BERT}} =
\frac{2 \cdot P_{\text{BERT}} \cdot R_{\text{BERT}}}{P_{\text{BERT}} +
R_{\text{BERT}}}\\]

BERTScore is useful because it can account for synonyms and paraphrasing.
Simpler metrics like BLEU and ROUGE can’t do this due to their reliance on
exact matches. BERTScore has been shown to have better correlation for tasks
such as image captioning and machine translation.

**[MoverScore](https://arxiv.org/abs/1909.02622)** also uses contextualized
embeddings to compute the distance between tokens in the generated output and
reference. But unlike BERTScore, which is based on one-to-one matching (or
“hard alignment”) of tokens, MoverScore allows for many-to-one matching (or
“soft alignment”).

![BERTScore \(left\) vs. MoverScore \(right\)](/assets/mover-score.jpg)

BERTScore (left) vs. MoverScore (right;
[source](https://arxiv.org/abs/1909.02622))

MoverScore enables the mapping of semantically related words in one sequence
to their counterparts in another sequence. It does this by solving a
constrained optimization problem that finds the minimum effort to transform
one text into another. The idea is to measure the distance that words would
have to move to convert one sequence to another.

However, there are several pitfalls to using these conventional benchmarks and
metrics.

First, there’s **poor correlation between these metrics and human judgments.**
BLEU, ROUGE, and others have had [negative correlation with how humans
evaluate fluency](https://arxiv.org/abs/2008.12009). They also showed moderate
to less correlation with human adequacy scores. In particular, BLEU and ROUGE
have [low correlation with tasks that require creativity and
diversity](https://arxiv.org/abs/2303.16634).

Second, these metrics often have **poor adaptability to a wider variety of
tasks**. Adopting a metric proposed for one task to another is not always
prudent. For example, exact match metrics such as BLEU and ROUGE are a poor
fit for tasks like abstractive summarization or dialogue. Since they’re based
on n-gram overlap between output and reference, they don’t make sense for a
dialogue task where a wide variety of responses are possible. An output can
have zero n-gram overlap with the reference but yet be a good response.

Third, these metrics have **poor reproducibility**. Even for the same metric,
[high variance is reported across different
studies](https://arxiv.org/abs/2008.12009), possibly due to variations in
human judgment collection or metric parameter settings. Another study of
[ROUGE scores](https://aclanthology.org/2023.acl-long.107/) across 2,000
studies found that scores were hard to reproduce, difficult to compare, and
often incorrect because evals were often conducted with untested, incorrect
ROUGE implementations.

![Dimensions of model evaluations with ROUGE](/assets/rogue-scores.jpg)

Dimensions of model evaluations with ROUGE
([source](https://aclanthology.org/2023.acl-long.107/))

And even with recent benchmarks such as MMLU, **the same model can get
significantly different scores based on the eval implementation**.
[Huggingface compared the original MMLU
implementation](https://huggingface.co/blog/evaluating-mmlu-leaderboard) with
the HELM and EleutherAI implementations and found that the same example could
have different prompts across various providers.

![Different prompts for the same question across MMLU
implementations](/assets/mmlu-prompt.jpg)

Different prompts for the same question across MMLU implementations
([source](https://huggingface.co/blog/evaluating-mmlu-leaderboard))

Furthermore, the evaluation approach differed across all three benchmarks:

  * Original MMLU: Compares predicted probabilities on the answers only (A, B, C, D)
  * HELM: Uses the next token probabilities from the model and picks the token with the highest probability, even if it’s _not_ one of the options.
  * EleutherAI: Computes probability of the full answer sequence (i.e., a letter followed by the answer text) for each answer. Then, pick answer with highest probability.

![Different eval for the same question across MMLU
implementations](/assets/mmlu-eval.jpg)

Different eval for the same question across MMLU implementations
([source](https://huggingface.co/blog/evaluating-mmlu-leaderboard))

As a result, even for the same eval, both absolute scores and model ranking
can fluctuate widely depending on eval implementation. This means that model
metrics aren’t truly comparable—even for the same eval—unless the eval’s
implementation is identical down to minute details like prompts and
tokenization. Similarly, the author of QLoRA found MMLU overly sensitive and
concluded: “[do not work with/report or trust MMLU
scores](https://twitter.com/Tim_Dettmers/status/1673446047266504704)”.

Beyond conventional evals such as those mentioned above, **an emerging trend
is to use a strong LLM as a reference-free metric** to evaluate generations
from other LLMs. This means we may not need human judgments or gold references
for evaluation.

**[G-Eval](https://arxiv.org/abs/2303.16634) is a framework that applies
LLMs** with Chain-of-Though (CoT) and a form-filling paradigm to **evaluate
LLM outputs**. First, they provide a task introduction and evaluation criteria
to an LLM and ask it to generate a CoT of evaluation steps. Then, to evaluate
coherence in news summarization, they concatenate the prompt, CoT, news
article, and summary and ask the LLM to output a score between 1 to 5.
Finally, they use the probabilities of the output tokens from the LLM to
normalize the score and take their weighted summation as the final result.

![Overview of G-Eval](/assets/geval.jpg)

Overview of G-Eval ([source](https://arxiv.org/abs/2303.16634))

They found that GPT-4 as an evaluator had a high Spearman correlation with
human judgments (0.514), outperforming all previous methods. It also
outperformed traditional metrics on aspects such as coherence, consistency,
fluency, and relevance. On topical chat, it did better than traditional
metrics such as ROUGE-L, BLEU-4, and BERTScore across several criteria such as
naturalness, coherence, engagingness, and groundedness.

**The[Vicuna](https://arxiv.org/abs/2306.05685) paper adopted a similar
approach.** They start by defining eight categories (writing, roleplay,
extraction, reasoning, math, coding, STEM, and humanities/social science)
before developing 10 questions for each category. Next, they generated answers
from five chatbots: LLaMA, Alpaca, ChatGPT, Bard, and Vicuna. Finally, they
asked GPT-4 to rate the quality of the answers based on helpfulness,
relevance, accuracy, and detail.

Overall, they found that GPT-4 not only provided consistent scores but could
also give detailed explanations for those scores. Under the single answer
grading paradigm, GPT-4 had higher agreement with humans (85%) than the humans
had amongst themselves (81%). This suggests that GPT-4’s judgment aligns
closely with the human evaluators.

**[QLoRA](https://arxiv.org/abs/2305.14314) also used an LLM to evaluate
another LLM’s output.** They asked GPT-4 to rate the performance of various
models against gpt-3.5-turbo on the Vicuna benchmark. Given the responses from
gpt-3.5-turbo and another model, GPT-4 was prompted to score both out of 10
and explain its ratings. They also measured performance via direct comparisons
between models, simplifying the task to a three-class rating scheme that
included ties.

To validate the automated evaluation, they collected human judgments on the
Vicuna benchmark. Using Mechanical Turk, they enlisted two annotators for
comparisons to gpt-3.5-turbo, and three annotators for pairwise comparisons.
They found that human and GPT-4 ranking of models were largely in agreement,
with a Spearman rank correlation of 0.55 at the model level. This provides an
additional data point suggesting that LLM-based automated evals could be a
cost-effective and reasonable alternative to human evals.

### How to apply evals?

**Building solid evals should be the starting point** for any LLM-based system
or product (as well as conventional machine learning systems).

Unfortunately, classical metrics such as BLEU and ROUGE don’t make sense for
more complex tasks such as abstractive summarization or dialogue. Furthermore,
we’ve seen that benchmarks like MMLU (and metrics like ROUGE) are sensitive to
how they’re implemented and measured. And to be candid, unless your LLM system
is studying for a school exam, using MMLU as an eval [doesn’t quite make
sense](https://twitter.com/Tim_Dettmers/status/1680782418335367169).

Thus, instead of using off-the-shelf benchmarks, we can **start by collecting
a set of task-specific evals** (i.e., prompt, context, expected outputs as
references). These evals will then guide prompt engineering, model selection,
fine-tuning, and so on. And as we update our systems, we can run these evals
to quickly measure improvements or regressions. Think of it as Eval Driven
Development (EDD).

In addition to the evaluation dataset, we **also need useful metrics**. They
help us distill performance changes into a single number that’s comparable
across eval runs. And if we can simplify the problem, we can choose metrics
that are easier to compute and interpret.

The simplest task is probably classification: If we’re using an LLM for
classification-like tasks (e.g., toxicity detection, document categorization)
or extractive QA without dialogue, we can rely on standard classification
metrics such as recall, precision, PRAUC, etc. If our task has no correct
answer but we have references (e.g., machine translation, extractive
summarization), we can rely on reference metrics based on matching (BLEU,
ROUGE) or semantic similarity (BERTScore, MoverScore).

However, these metrics may not work for more open-ended tasks such as
abstractive summarization, dialogue, and others. But collecting human
judgments can be slow and expensive. Thus, we may opt to lean on **automated
evaluations via a strong LLM**.

Relative to human judgments which are typically noisy (due to differing biases
among annotators), LLM judgments tend to be less noisy (as the bias is more
systematic) but more biased. Nonetheless, since we’re aware of these biases,
we can mitigate them accordingly:

  * Position bias: LLMs tend to favor the response in the first position. To mitigate this, we can evaluate the same pair of responses twice while swapping their order. If the same response is preferred in both orders, we mark it as a win; else, it’s a tie.
  * Verbosity bias: LLMs tend to favor longer, wordier responses over more concise ones, even if the latter is clearer and of higher quality. A possible solution is to ensure that comparison responses are similar in length.
  * Self-enhancement bias: LLMs have a slight bias towards their own answers. [GPT-4 favors itself with a 10% higher win rate while Claude-v1 favors itself with a 25% higher win rate.](https://arxiv.org/abs/2306.05685) To counter this, don’t use the same LLM for evaluation tasks.

Another tip: Rather than asking an LLM for a direct evaluation (via giving a
score), try giving it a reference and asking for a comparison. This helps with
reducing noise.

Finally, sometimes the best eval is human eval aka vibe check. (Not to be
confused with the poorly named code evaluation benchmark
[HumanEval](https://arxiv.org/abs/2107.03374).) As mentioned in the [Latent
Space podcast with MosaicML](https://www.latent.space/p/mosaic-mpt-7b#details)
(34th minute):

> The vibe-based eval cannot be underrated. … One of our evals was just having
> a bunch of prompts and watching the answers as the models trained and see if
> they change. Honestly, I don’t really believe that any of these eval metrics
> capture what we care about. One of our prompts was “suggest games for a
> 3-year-old and a 7-year-old to play” and that was a lot more valuable to see
> how the answer changed during the course of training. — Jonathan Frankle

Also see this [deep dive into evals](/writing/abstractive/) for abstractive
summarization. It covers reference, context, and preference-based metrics, and
also discusses hallucination detection.

## Retrieval-Augmented Generation: To add knowledge

Retrieval-Augmented Generation (RAG) fetches relevant data from outside the
foundation model and enhances the input with this data, providing richer
context to improve output.

### Why RAG?

RAG helps reduce hallucination by grounding the model on the retrieved
context, thus increasing factuality. In addition, it’s cheaper to keep
retrieval indices up-to-date than to continuously pre-train an LLM. This cost
efficiency makes it easier to provide LLMs with access to recent data via RAG.
Finally, if we need to update or remove data such as biased or toxic
documents, it’s more straightforward to update the retrieval index (compared
to fine-tuning or prompting an LLM not to generate toxic outputs).

In short, RAG applies mature and simpler ideas from the field of information
retrieval to support LLM generation. In a [recent Sequoia
survey](https://www.sequoiacap.com/article/llm-stack-perspective/), 88% of
respondents believe that retrieval will be a key component of their stack.

### More about RAG

Before diving into RAG, it helps to have a basic understanding of text
embeddings. (Feel free to skip this section if you’re familiar with the
subject.)

A text embedding is a **compressed, abstract representation of text data**
where text of arbitrary length can be represented as a fixed-size vector of
numbers. It’s usually learned from a corpus of text such as Wikipedia. Think
of them as a universal encoding for text, where **similar items are close to
each other while dissimilar items are farther apart**.

A good embedding is one that does well on a downstream task, such as
retrieving similar items. Huggingface’s [Massive Text Embedding Benchmark
(MTEB)](https://huggingface.co/spaces/mteb/leaderboard) scores various models
on diverse tasks such as classification, clustering, retrieval, summarization,
etc.

Quick note: While we mainly discuss text embeddings here, embeddings can take
many modalities. For example, [CLIP](https://arxiv.org/abs/2103.00020) is
multimodal and embeds images and text in the same space, allowing us to find
images most similar to an input text. We can also [embed products based on
user behavior](/writing/search-query-matching/#supervised-techniques-improves-
modeling-of-our-desired-event) (e.g., clicks, purchases) or [graph
relationships](/writing/search-query-matching/#self-supervised-techniques-no-
need-for-labels).

**RAG has its roots in open-domain Q &A.** An early [Meta
paper](https://arxiv.org/abs/2005.04611) showed that retrieving relevant
documents via TF-IDF and providing them as context to a language model (BERT)
improved performance on an open-domain QA task. They converted each task into
a cloze statement and queried the language model for the missing token.

Following that, **[Dense Passage Retrieval
(DPR)](https://arxiv.org/abs/2004.04906)** showed that using dense embeddings
(instead of a sparse vector space such as TF-IDF) for document retrieval can
outperform strong baselines like Lucene BM25 (65.2% vs. 42.9% for top-5
accuracy.) They also showed that higher retrieval precision translates to
higher end-to-end QA accuracy, highlighting the importance of upstream
retrieval.

To learn the DPR embedding, they fine-tuned two independent BERT-based
encoders on existing question-answer pairs. The passage encoder (\\(E_p\\))
embeds text passages into vectors while the query encoder (\\(E_q\\)) embeds
questions into vectors. The query embedding is then used to retrieve \\(k\\)
passages that are most similar to the question.

They trained the encoders so that the dot-product similarity makes a good
ranking function, and optimized the loss function as the negative log-
likelihood of the positive passage. The DPR embeddings are optimized for
maximum inner product between the question and relevant passage vectors. The
goal is to learn a vector space such that pairs of questions and their
relevant passages are close together.

For inference, they embed all passages (via \\(E_p\\)) and index them in FAISS
offline. Then, given a question at query time, they compute the question
embedding (via \\(E_q\\)), retrieve the top \\(k\\) passages via approximate
nearest neighbors, and provide it to the language model (BERT) that outputs
the answer to the question.

**[Retrieval Augmented Generation (RAG)](https://arxiv.org/abs/2005.11401)** ,
from which this pattern gets its name, highlighted the downsides of pre-
trained LLMs. These include not being able to expand or revise memory, not
providing insights into generated output, and hallucinations.

To address these downsides, they introduced RAG (aka semi-parametric models).
Dense vector retrieval serves as the non-parametric component while a pre-
trained LLM acts as the parametric component. They reused the DPR encoders to
initialize the retriever and build the document index. For the LLM, they used
BART, a 400M parameter seq2seq model.

![Overview of Retrieval Augmented Generation](/assets/rag.jpg)

Overview of Retrieval Augmented Generation
([source](https://arxiv.org/abs/2005.11401))

During inference, they concatenate the input with the retrieved document.
Then, the LLM generates \\(\text{token}_i\\) based on the original input, the
retrieved document, and the previous \\(i-1\\) tokens. For generation, they
proposed two approaches that vary in how the retrieved passages are used to
generate output.

In the first approach, RAG-Sequence, the model uses the same document to
generate the complete sequence. Thus, for \\(k\\) retrieved documents, the
generator produces an output for each document. Then, the probability of each
output sequence is marginalized (sum the probability of each output sequence
in \\(k\\) and weigh it by the probability of each document being retrieved).
Finally, the output sequence with the highest probability is selected.

On the other hand, RAG-Token can generate each token based on a _different_
document. Given \\(k\\) retrieved documents, the generator produces a
distribution for the next output token for each document before marginalizing
(aggregating all the individual token distributions.). The process is then
repeated for the next token. This means that, for each token generation, it
can retrieve a different set of \\(k\\) relevant documents based on the
original input _and_ previously generated tokens. Thus, documents can have
different retrieval probabilities and contribute differently to the next
generated token.

[**Fusion-in-Decoder (FiD)**](https://arxiv.org/abs/2007.01282) also uses
retrieval with generative models for open-domain QA. It supports two methods
for retrieval, BM25 (Lucene with default parameters) and DPR. FiD is named for
how it performs fusion on the retrieved documents in the decoder only.

![Overview of Fusion-in-Decoder](/assets/fid.jpg)

Overview of Fusion-in-Decoder ([source](https://arxiv.org/abs/2007.01282))

For each retrieved passage, the title and passage are concatenated with the
question. These pairs are processed independently in the encoder. They also
add special tokens such as `question:`, `title:`, and `context:` before their
corresponding sections. The decoder attends over the concatenation of these
retrieved passages.

Because it processes passages independently in the encoder, it can scale to a
large number of passages as it only needs to do self-attention over one
context at a time. Thus, compute grows linearly (instead of quadratically)
with the number of retrieved passages, making it more scalable than
alternatives such as RAG-Token. Then, during decoding, the decoder processes
the encoded passages jointly, allowing it to better aggregate context across
multiple retrieved passages.

[**Retrieval-Enhanced Transformer (RETRO)**](https://arxiv.org/abs/2112.04426)
adopts a similar pattern where it combines a frozen BERT retriever, a
differentiable encoder, and chunked cross-attention to generate output. What’s
different is that RETRO does retrieval throughout the entire pre-training
stage, and not just during inference. Furthermore, they fetch relevant
documents based on chunks of the input. This allows for finer-grained,
repeated retrieval during generation instead of only retrieving once per
query.

For each input chunk (\\(C_u\\)), the \\(k\\) retrieved chunks \\(RET(C_u)\\)
are fed into an encoder. The output is the encoded neighbors \\(E^{j}_{u}\\)
where \\(E^{j}_{u} = \text{Encoder}(\text{RET}(C_{u})^{j}, H_{u}) \in
\mathbb{R}^{r \times d_{0}}\\). Here, each chunk encoding is conditioned on
\\(H_u\\) (the intermediate activations) and the activations of chunk
\\(C_u\\) through cross-attention layers. In short, the encoding of the
retrieved chunks depends on the attended activation of the input chunk.
\\(E^{j}_{u}\\) is then used to condition the generation of the next chunk.

![Overview of RETRO](/assets/retro.jpg)

Overview of RETRO ([source](https://arxiv.org/abs/2112.04426))

During retrieval, RETRO splits the input sequence into chunks of 64 tokens.
Then, it finds text similar to the _previous_ chunk to provide context to the
_current_ chunk. The retrieval index consists of two contiguous chunks of
tokens, \\(N\\) and \\(F\\). The former is the neighbor chunk (64 tokens)
which is used to compute the key while the latter is the continuation chunk
(64 tokens) in the original document.

Retrieval is based on approximate \\(k\\)-nearest neighbors via \\(L_2\\)
distance (euclidean) on BERT embeddings. (Interesting departure from the usual
cosine or dot product similarity.) The retrieval index, built on SCaNN, can
query a 2T token database in 10ms.

They also demonstrated how to RETRO-fit existing baseline models. By freezing
the pre-trained weights and only training the chunked cross-attention and
neighbor encoder parameters (< 10% of weights for a 7B model), they can
enhance transformers with retrieval while only requiring 6M training sequences
(3% of pre-training sequences). RETRO-fitted models were able to surpass the
performance of baseline models and achieve performance close to that of RETRO
trained from scratch.

![Performance from RETRO-fitting a pre-trained model](/assets/retrofit.jpg)

Performance from RETRO-fitting a pre-trained model
([source](https://arxiv.org/abs/2112.04426))

**[Internet-augmented LMs](https://arxiv.org/abs/2203.05115)** proposes using
a humble “off-the-shelf” search engine to augment LLMs. First, they retrieve a
set of relevant documents via Google Search. Since these retrieved documents
tend to be long (average length 2,056 words), they chunk them into paragraphs
of six sentences each. Finally, they embed the question and paragraphs via TF-
IDF and applied cosine similarity to rank the most relevant paragraphs for
each query.

![Overview of internet-augmented LLMs](/assets/internet-llm.jpg)

Overview of internet-augmented LLMs
([source](https://arxiv.org/abs/2203.05115))

The retrieved paragraphs are used to condition the LLM via few-shot prompting.
They adopt the conventional \\(k\\)-shot prompting (\\(k=15\\)) from closed-
book QA (only providing question-answer pairs) and extend it with an evidence
paragraph, such that each context is an evidence, question, and answer
triplet.

For the generator, they used Gopher, a 280B parameter model trained on 300B
tokens. For each question, they generated four candidate answers based on each
of the 50 retrieved paragraphs. Finally, they select the best answer by
estimating the answer probability via several methods including direct
inference, RAG, noisy channel inference, and Product-of-Experts (PoE). PoE
consistently performed the best.

RAG has also been **applied to non-QA tasks such as code generation**. While
**[CodeT5+](https://arxiv.org/abs/2305.07922)** can be used as a standalone
generator, when combined with RAG, it significantly outperforms similar models
in code generation.

To assess the impact of RAG on code generation, they evaluate the model in
three settings:

  * Retrieval-based: Fetch the top-1 code sample as the prediction
  * Generative-only: Output code based on the decoder only
  * Retrieval-augmented: Append top-1 code sample to encoder input before code generation via the decoder.

![>Overview of RAG for CodeT5+](/assets/codet5.jpg)

Overview of RAG for CodeT5+ ([source](https://arxiv.org/abs/2305.07922))

As a qualitative example, they showed that retrieved code provides crucial
context (e.g., use `urllib3` for an HTTP request) and guides the generative
process towards more correct predictions. In contrast, the generative-only
approach returns incorrect output that only captures the concepts of
“download” and “compress”.

**What if we don’t have relevance judgments for query-passage pairs?** Without
them, we would not be able to train the bi-encoders that embed the queries and
documents in the same embedding space where relevance is represented by the
inner product. **[Hypothetical document embeddings
(HyDE)](https://arxiv.org/abs/2212.10496)** suggests a solution.

![Overview of HyDE](/assets/hyde.jpg)

Overview of HyDE ([source](https://arxiv.org/abs/2212.10496))

Given a query, HyDE first prompts an LLM, such as InstructGPT, to generate a
hypothetical document. Then, an unsupervised encoder, such as Contriver,
encodes the document into an embedding vector. Finally, the inner product is
computed between the _hypothetical_ document and the corpus, and the most
similar _real_ documents are retrieved.

The expectation is that the encoder’s dense bottleneck serves as a lossy
compressor and the extraneous, non-factual details are excluded via the
embedding. This reframes the relevance modeling problem from a representation
learning task to a generation task.

### How to apply RAG

From experience with [Obsidian-Copilot](/writing/obsidian-copilot/), I’ve
found that hybrid retrieval (traditional search index + embedding-based
search) works better than either alone. There, I complemented classical
retrieval (BM25 via OpenSearch) with semantic search (`e5-small-v2`).

Why not embedding-based search only? While it’s great in many instances, there
are situations where it falls short, such as:

  * Searching for a person or object’s name (e.g., Eugene, Kaptir 2.0)
  * Searching for an acronym or phrase (e.g., RAG, RLHF)
  * Searching for an ID (e.g., `gpt-3.5-turbo`, `titan-xlarge-v1.01`)

But keyword search has its limitations too. It only models simple word
frequencies and doesn’t capture semantic or correlation information. Thus, it
doesn’t deal well with synonyms or hypernyms (i.e., words that represent a
generalization). This is where combining it with semantic search is
complementary.

In addition, with a conventional search index, we can use metadata to refine
results. For example, we can use date filters to prioritize newer documents or
narrow our search to a specific time period. And if the search is related to
e-commerce, filters on average rating or categories are helpful. Finally,
having metadata is handy for downstream ranking, such as prioritizing
documents that are cited more, or boosting products by their sales volume.

**With regard to embeddings** , the seemingly popular approach is to use
[`text-embedding-ada-002`](https://openai.com/blog/new-and-improved-embedding-
model). Its benefits include ease of use via an API and not having to maintain
our own embedding infra or self-host embedding models. Nonetheless, personal
experience and anecdotes from others suggest there are better alternatives for
retrieval.

The OG embedding approaches include Word2vec and
[fastText](https://fasttext.cc). FastText is an open-source, lightweight
library that enables users to leverage pre-trained embeddings or train new
embedding models. It comes with pre-trained embeddings for 157 languages and
is extremely fast, even without a GPU. It’s my go-to for early-stage proof of
concepts.

Another good baseline is [sentence-
transformers](https://github.com/UKPLab/sentence-transformers). It makes it
simple to compute embeddings for sentences, paragraphs, and even images. It’s
based on workhorse transformers such as BERT and RoBERTa and is available in
more than 100 languages.

More recently, instructor models have shown SOTA performance. During training,
these models prepend the task description to the text. Then, when embedding
new text, we simply have to describe the task to get task-specific embeddings.
(Not that different from instruction tuning for embedding models IMHO.)

An example is the [E5](https://arxiv.org/abs/2212.03533) family of models. For
open QA and information retrieval, we simply prepend documents in the index
with `passage:`, and prepend queries with `query:`. If the task is symmetric
(e.g., semantic similarity, paraphrase retrieval) or if we want to use
embeddings as features (e.g., classification, clustering), we just use the
`query:` prefix.

The [Instructor](https://arxiv.org/abs/2212.09741) model takes it a step
further, allowing users to customize the prepended prompt: “Represent the
`domain` `task_type` for the `task_objective`:” For example, “Represent the
Wikipedia document for retrieval:”. (The domain and task objective are
optional). This brings the concept of prompt tuning into the field of text
embedding.

Finally, as of Aug 1st, the top embedding model on the [MTEB
Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) is the
[GTE](https://huggingface.co/thenlper/gte-large) family of models by Alibaba
DAMO Academy. The top performing model’s size is half of the next best model
`e5-large-v2` (0.67GB vs 1.34GB). In 2nd position is `gte-base` with a model
size of only 0.22GB and embedding dimension of 768. (H/T
[Nirant](https://twitter.com/NirantK).)

To retrieve documents with low latency at scale, we use approximate nearest
neighbors (ANN). It optimizes for retrieval speed and returns the approximate
(instead of exact) top \\(k\\) most similar neighbors, trading off a little
accuracy loss for a large speed up.

ANN embedding indices are data structures that let us do ANN searches
efficiently. At a high level, they build partitions over the embedding space
so we can quickly zoom in on the specific space where the query vector is.
Some popular techniques include:

  * [Locality Sensitive Hashing](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) (LSH): The core idea is to create hash functions so that similar items are likely to end up in the same hash bucket. By only needing to check the relevant buckets, we can perform ANN queries efficiently.
  * [Facebook AI Similarity Search](https://github.com/facebookresearch/faiss) (FAISS): It uses a combination of quantization and indexing for efficient retrieval, supports both CPU and GPU, and can handle billions of vectors due to its efficient use of memory.
  * [Hierarchical Navigable Small Worlds](https://github.com/nmslib/hnswlib) (HNSW): Inspired by “six degrees of separation”, it builds a hierarchical graph structure that embodies the small world phenomenon. Here, most nodes can be reached from any other node via a minimum number of hops. This structure allows HNSW to initiate queries from broader, coarser approximations and progressively narrow the search at lower levels.
  * [Scalable Nearest Neighbors](https://github.com/google-research/google-research/tree/master/scann) (ScaNN): It has a two-step process. First, coarse quantization reduces the search space. Then, fine-grained search is done within the reduced set. Best recall/latency trade-off I’ve seen.

When evaluating an ANN index, some factors to consider include:

  * Recall: How does it fare against exact nearest neighbors?
  * Latency/throughput: How many queries can it handle per second?
  * Memory footprint: How much RAM is required to serve an index?
  * Ease of adding new items: Can new items be added without having to reindex all documents (LSH) or does the index need to be rebuilt (ScaNN)?

No single framework is better than all others in every aspect. Thus, start by
defining your functional and non-functional requirements before benchmarking.
Personally, I’ve found ScaNN to be outstanding in the recall-latency trade-off
(see benchmark graph [here](/writing/real-time-recommendations/#how-to-design-
and-implement-an-mvp)).

## Fine-tuning: To get better at specific tasks

Fine-tuning is the process of taking a pre-trained model (that has already
been trained with a vast amount of data) and further refining it on a specific
task. The intent is to harness the knowledge that the model has already
acquired during its pre-training and apply it to a specific task, usually
involving a smaller, task-specific, dataset.

The term “fine-tuning” is used loosely and can refer to several concepts such
as:

  * **Continued pre-training** : With domain-specific data, apply the same pre-training regime (next token prediction, masked language modeling) on the base model.
  * **Instruction fine-tuning** : The pre-trained (base) model is fine-tuned on examples of instruction-output pairs to follow instructions, answer questions, be waifu, etc.
  * **Single-task fine-tuning** : The pre-trained model is honed for a narrow and specific task such as toxicity detection or summarization, similar to BERT and T5.
  * **Reinforcement learning with human feedback (RLHF)** : This combines instruction fine-tuning with reinforcement learning. It requires collecting human preferences (e.g., pairwise comparisons) which are then used to train a reward model. The reward model is then used to further fine-tune the instructed LLM via RL techniques such as proximal policy optimization (PPO).

We’ll mainly focus on single-task and instruction fine-tuning here.

### Why fine-tuning?

Fine-tuning an open LLM is becoming an increasingly viable alternative to
using a 3rd-party, cloud-based LLM for several reasons.

**Performance & control:** Fine-tuning can improve the performance of an off-
the-shelf base model, and may even surpass a 3rd-party LLM. It also provides
greater control over LLM behavior, resulting in a more robust system or
product. Overall, fine-tuning enables us to build products that are
differentiated from simply using 3rd-party or open LLMs.

**Modularization:** Single-task fine-tuning lets us to use an army of smaller
models that each specialize on their own tasks. Via this setup, a system can
be modularized into individual models for tasks like content moderation,
extraction, summarization, etc. Also, given that each model only has to focus
on a narrow set of tasks, we can get around the alignment tax, where fine-
tuning a model on one task reduces performance on other tasks.

**Reduced dependencies:** By fine-tuning and hosting our own models, we can
reduce legal concerns about proprietary data (e.g., PII, internal documents
and code) being exposed to external APIs. It also gets around constraints that
come with 3rd-party LLMs such as rate-limiting, high costs, or overly
restrictive safety filters. By fine-tuning and hosting our own LLMs, we can
ensure data doesn’t leave our network, and can scale throughput as needed.

### More about fine-tuning

Why do we need to fine-tune a _base_ model? At the risk of oversimplifying,
base models are primarily optimized to predict the next word based on the
corpus they’re trained on. Hence, they aren’t naturally adept at following
instructions or answering questions. When posed a question, they tend to
respond with more questions. Thus, we perform instruction fine-tuning so they
learn to respond appropriately.

However, fine-tuning isn’t without its challenges. First, we **need a
significant volume of demonstration data**. For instance, in the [InstructGPT
paper](https://arxiv.org/abs/2203.02155), they used 13k instruction-output
samples for supervised fine-tuning, 33k output comparisons for reward
modeling, and 31k prompts without human labels as input for RLHF.

Furthermore, fine-tuning comes with an alignment tax—the process can lead to
**lower performance on certain critical tasks**. (There’s no free lunch after
all.) The same InstructGPT paper found that RLHF led to performance
regressions (relative to the GPT-3 base model) on public NLP tasks like SQuAD,
HellaSwag, and WMT 2015 French to English. (A workaround is to have several
smaller, specialized models that excel at narrow tasks.)

Fine-tuning is similar to the concept of transfer learning. As defined in
Wikipedia: “Transfer learning is a technique in machine learning in which
knowledge learned from a task is re-used to boost performance on a related
task.” Several years ago, transfer learning made it easy for me to apply
ResNet models trained on ImageNet to [classify fashion
products](/writing/image-categorization-is-now-live/) and [build image
search](/writing/image-search-is-now-live/).

**[ULMFit](https://arxiv.org/abs/1801.06146)** is one of the earlier papers to
apply transfer learning to text. They established the protocol of self-
supervised pre-training (on unlabeled data) followed by fine-tuning (on
labeled data). They used AWS-LSTM, an LSTM variant with dropout at various
gates.

![Overview of ULMFit](/assets/ulmfit.jpg)

Overview of ULMFit ([source](https://arxiv.org/abs/1801.06146))

During pre-training (next word prediction), the model is trained on
wikitext-103 which contains 28.6 Wikipedia articles and 103M words. Then,
during target task fine-tuning, the LM is fine-tuned with data from the domain
of the specific task. Finally, during classifier fine-tuning, the model is
augmented with two additional linear blocks and fine-tuned on the target
classification tasks which includes sentiment analysis, question
classification, and topic classification.

Since then, the pre-training followed by fine-tuning paradigm has driven much
progress in language modeling. **[Bidirectional Encoder Representations from
Transformers (BERT; encoder only)](https://arxiv.org/abs/1810.04805)** was
pre-trained on masked language modeling and next sentence prediction on
English Wikipedia and BooksCorpus. It was then fine-tuned on task-specific
inputs and labels for single-sentence classification, sentence pair
classification, single-sentence tagging, and question & answering.

![Overview of BERT](/assets/bert.jpg)

Overview of BERT ([source](https://arxiv.org/abs/1810.04805))

**[Generative Pre-trained Transformers (GPT; decoder only)](https://s3-us-
west-2.amazonaws.com/openai-assets/research-covers/language-
unsupervised/language_understanding_paper.pdf)** was first pre-trained on
BooksCorpus via next token prediction. This was followed by single-task fine-
tuning for tasks such as text classification, textual entailment, similarity,
and Q&A. Interestingly, they found that including language modeling as an
auxiliary objective helped the model generalize and converge faster during
training.

![Overview of GPT](/assets/gpt.jpg)

Overview of GPT ([source](https://s3-us-west-2.amazonaws.com/openai-
assets/research-covers/language-unsupervised/language_understanding_paper.pd))

**[Text-to-text Transfer Transformer (T5; encoder-
decoder)](https://arxiv.org/abs/1910.10683)** was pre-trained on the Colossal
Clean Crawled Corpus (C4), a cleaned version of the Common Crawl from April
2019. It employed the same denoising objective as BERT, namely masked language
modeling. It was then fine-tuned on tasks such as text classification,
abstractive summarization, Q&A, and machine translation.

![Overview of T5](/assets/t5.jpg)

Overview of T5 ([source](https://arxiv.org/abs/1910.10683))

But unlike ULMFIt, BERT, and GPT which used different classifier heads for
downstream tasks, T5 represented downstream tasks as text-to-text only. For
example, a translation task would have input text starting with `Translation
English to German:`, while a summarization task might start with `Summarize:`
or `TL;DR:`. The prefix essentially became a hyperparameter (first instance of
prompt engineering?) This design choice allowed them to use a single fine-
tuned model across a variety of downstream tasks.

**[InstructGPT](https://arxiv.org/abs/2203.02155)** expanded this idea of
single-task fine-tuning to instruction fine-tuning. The base model was GPT-3,
pre-trained on internet data including Common Crawl, WebText, Books, and
Wikipedia. It then applied supervised fine-tuning on demonstrations of desired
behavior (instruction and output). Next, it trained a reward model on the
dataset of comparisons. Finally, it optimized the instructed model against the
reward model via PPO, with this last stage focusing more on alignment than
specific task performance.

![Overview of fine-tuning steps in InstructGPT](/assets/instructgpt.jpg)

Overview of fine-tuning steps in InstructGPT
([source](https://arxiv.org/abs/2203.02155))

Next, let’s move from fine-tuned models to fine-tuning techniques.

**[Soft prompt tuning](https://arxiv.org/abs/2104.08691)** prepends a
trainable tensor to the model’s input embeddings, essentially creating a soft
prompt. Unlike discrete text prompts, soft prompts can be learned via
backpropagation, meaning they can be fine-tuned to incorporate signals from
any number of labeled examples.

Next, there’s **[prefix tuning](https://arxiv.org/abs/2101.00190)**. Instead
of adding a soft prompt to the model input, it prepends trainable parameters
to the hidden states of all transformer blocks. During fine-tuning, the LM’s
original parameters are kept frozen while the prefix parameters are updated.

![Overview of prefix-tuning](/assets/prefix.jpg)

Overview of prefix-tuning ([source](https://arxiv.org/abs/2101.00190))

The paper showed that this achieved performance comparable to full fine-tuning
despite requiring updates on just 0.1% of parameters. Moreover, in settings
with limited data and involved extrapolation to new topics, it outperformed
full fine-tuning. One hypothesis is that training fewer parameters helped
reduce overfitting on smaller target datasets.

There’s also the **[adapter](https://arxiv.org/abs/1902.00751)** technique.
This method adds fully connected network layers twice to each transformer
block, after the attention layer and after the feed-forward network layer. On
GLUE, it’s able to achieve within 0.4% of the performance of full fine-tuning
by just adding 3.6% parameters per task.

![Overview of adapters](/assets/adapter.jpg)

Overview of adapters ([source](https://arxiv.org/abs/1902.00751))

**[Low-Rank Adaptation (LoRA)](https://arxiv.org/abs/2106.09685)** is a
technique where adapters are designed to be the product of two low-rank
matrices. It was inspired by [Aghajanyan et
al.](https://arxiv.org/abs/2012.13255) which showed that, when adapting to a
specific task, pre-trained language models have a low intrinsic dimension and
can still learn efficiently despite a random projection into a smaller
subspace. Thus, LoRA hypothesized that weight updates during adaption also
have low intrinsic rank.

![Overview of LoRA](/assets/lora.jpg)

Overview of LoRA ([source](https://arxiv.org/abs/2106.09685))

Similar to prefix tuning, they found that LoRA outperformed several baselines
including full fine-tuning. Again, the hypothesis is that LoRA, thanks to its
reduced rank, provides implicit regularization. In contrast, full fine-tuning,
which updates all weights, could be prone to overfitting.

**[QLoRA](https://arxiv.org/abs/2305.14314)** builds on the idea of LoRA. But
instead of using the full 16-bit model during fine-tuning, it applies a 4-bit
quantized model. It introduced several innovations such as 4-bit NormalFloat
(to quantize models), double quantization (for additional memory savings), and
paged optimizers (that prevent OOM errors by transferring data to CPU RAM when
the GPU runs out of memory).

![Overview of QLoRA](/assets/qlora.jpg)

Overview of QLoRA ([source](https://arxiv.org/abs/2305.14314))

As a result, QLoRA reduces the average memory requirements for fine-tuning a
65B model from > 780GB memory to a more manageable 48B without degrading
runtime or predictive performance compared to a 16-bit fully fine-tuned
baseline.

(Fun fact: During a meetup with Tim Dettmers, an author of QLoRA, he quipped
that double quantization was “a bit of a silly idea but works perfectly.” Hey,
if it works, it works.)

### How to apply fine-tuning?

The first step is to **collect demonstration data/labels**. These could be for
straightforward tasks such as document classification, entity extraction, or
summarization, or they could be more complex such as Q&A or dialogue. Some
ways to collect this data include:

  * **Via experts or crowd-sourced human annotators** : While this is expensive and slow, it usually leads to higher-quality data with [good guidelines](/writing/labeling-guidelines/).
  * **Via user feedback** : This can be as simple as asking users to select attributes that describe a product, rating LLM responses with thumbs up or down (e.g., ChatGPT), or logging which images users choose to download (e.g., Midjourney).
  * **Query larger open models with permissive licenses** : With prompt engineering, we might be able to elicit reasonable demonstration data from a larger model (Falcon 40B Instruct) that can be used to fine-tune a smaller model.
  * **Reuse open-source data** : If your task can be framed as a natural language inference (NLI) task, we could fine-tune a model to perform NLI using [MNLI data](https://cims.nyu.edu/~sbowman/multinli/). Then, we can continue fine-tuning the model on internal data to classify inputs as entailment, neutral, or contradiction.

Note: Some LLM terms prevent users from using their output to develop other
models.

  * [OpenAI Terms of Use](https://openai.com/policies/terms-of-use) (Section 2c, iii): You may not use output from the Services to develop models that compete with OpenAI.
  * [LLaMA 2 Community License Agreement](https://ai.meta.com/llama/license/) (Section 1b-v): You will not use the Llama Materials or any output or results of the Llama Materials to improve any other large language model (excluding Llama 2 or derivative works thereof).

The next step is to **define evaluation metrics**. We’ve discussed this in a
previous section.

Then, **select a pre-trained model.** There are [several open LLMs with
permissive licenses](https://github.com/eugeneyan/open-llms) to choose from.
Excluding Llama 2 (since it isn’t fully commercial use), Falcon-40B is known
to be the best-performing model. Nonetheless, I’ve found it unwieldy to fine-
tune and serve in production given how heavy it is.

Instead, I’m inclined to use smaller models like the Falcon-7B. And if we can
simplify and frame the task more narrowly, BERT (340M params), RoBERTA (355M
params), and BART (406M params) are solid picks for classification and natural
language inference tasks. Beyond that, Flan-T5 (770M and 3B variants) is a
reliable baseline for translation, abstractive summarization, headline
generation, etc.

We may also need to **update the model architecture** , such as when the pre-
trained model’s architecture doesn’t align with the task. For example, we
might need to update the classification heads on BERT or T5 to match our task.
Tip: If the task is a simple binary classification task, NLI models can work
out of the box. Entailment is mapped to positive, contradiction is mapped to
negative, while the neural label can indicate uncertainty.

**Then, pick a fine-tuning approach.** LoRA and QLoRA are good places to
start. But if your fine-tuning is more intensive, such as continued pre-
training on new domain knowledge, you may find full fine-tuning necessary.

**Finally, basic hyperparameter tuning.** Generally, most papers focus on
learning rate, batch size, and number of epochs (see LoRA, QLoRA). And if
we’re using LoRA, we might want to tune the rank parameter (though the QLoRA
paper found that different rank and alpha led to similar results). Other
hyperparameters include input sequence length, loss type (contrastive loss vs.
token match), and data ratios (like the mix of pre-training or demonstration
data, or the ratio of positive to negative examples, among others).

## Caching: To reduce latency and cost

Caching is a technique to store data that has been previously retrieved or
computed. This way, future requests for the same data can be served faster. In
the space of serving LLM generations, the popularized approach is to cache the
LLM response keyed on the embedding of the input request. Then, for each new
request, if a semantically similar request is received, we can serve the
cached response.

For some practitioners, this sounds like “[a disaster waiting to
happen.](https://twitter.com/HanchungLee/status/1681146845186363392)” I’m
inclined to agree. Thus, I think the key to adopting this pattern is figuring
out how to cache safely, instead of solely depending on semantic similarity.

### Why caching?

Caching can significantly reduce latency for responses that have been served
before. In addition, by eliminating the need to compute a response for the
same input again and again, we can reduce the number of LLM requests and thus
save cost. Also, there are certain use cases that do not support latency on
the order of seconds. Thus, pre-computing and caching may be the only way to
serve those use cases.

### More about caching

A cache is a high-speed storage layer that stores a subset of data that’s
accessed more frequently. This lets us serve these requests faster via the
cache instead of the data’s primary storage (e.g., search index, relational
database). Overall, caching enables efficient reuse of previously fetched or
computed data. (More about [caching](https://aws.amazon.com/caching/) and
[best practices](https://aws.amazon.com/caching/best-practices/).)

An example of caching for LLMs is
[GPTCache](https://github.com/zilliztech/GPTCache).

![Overview of GPTCache](/assets/gptcache.jpg)

Overview of GPTCache ([source](https://github.com/zilliztech/GPTCache))

When a new request is received:

  * Embedding generator: This embeds the request via various models such as OpenAI’s `text-embedding-ada-002`, FastText, Sentence Transformers, and more.
  * Similarity evaluator: This computes the similarity of the request via the vector store and then provides a distance metric. The vector store can either be local (FAISS, Hnswlib) or cloud-based. It can also compute similarity via a model.
  * Cache storage: If the request is similar, the cached response is fetched and served.
  * LLM: If the request isn’t similar enough, it gets passed to the LLM which then generates the result. Finally, the response is served and cached for future use.

Redis also shared a [similar
example](https://www.youtube.com/live/9VgpXcfJYvw?feature=share&t=1517),
mentioning that some teams go as far as precomputing all the queries they
anticipate receiving. Then, they set a similarity threshold on which queries
are similar enough to warrant a cached response.

### How to apply caching?

**We should start with having a good understanding of user request patterns**.
This allows us to design the cache thoughtfully so it can be applied reliably.

First, let’s consider a non-LLM example. Imagine we’re caching product prices
for an e-commerce site. During checkout, is it safe to display the (possibly
outdated) cached price? Probably not, since the price the customer sees during
checkout should be the same as the final amount they’re charged. Caching isn’t
appropriate here as we need to ensure consistency for the customer.

Now, bringing it back to LLM responses. Imagine we get a request for a summary
of “Mission Impossible 2” that’s semantically similar enough to “Mission
Impossible 3”. If we’re looking up cache based on semantic similarity, we
could serve the wrong response.

We also need to **consider if caching is effective for the usage pattern.**
One way to quantify this is via the cache hit rate (percentage of requests
served directly from the cache). If the usage pattern is uniformly random, the
cache would need frequent updates. Thus, the effort to keep the cache up-to-
date could negate any benefit a cache has to offer. On the other hand, if the
usage follows a power law where a small proportion of unique requests account
for the majority of traffic (e.g., search queries, product views), then
caching could be an effective strategy.

Beyond semantic similarity, we could also explore caching based on:

  * **Item IDs:** This applies when we pre-compute [summaries of product reviews](https://www.cnbc.com/2023/06/12/amazon-is-using-generative-ai-to-summarize-product-reviews.html) or generate a summary for an entire movie trilogy.
  * **Pairs of Item IDs:** Such as when we generate comparisons between two movies. While this appears to be \\(O(N^2)\\), in practice, a small number of combinations drive the bulk of traffic, such as comparison between popular movies in a series or genre.
  * **Constrained input:** Such as variables like movie genre, director, or lead actor. For example, if a user is looking for movies by a specific director, we could execute a structured query and run it through an LLM to frame the response more eloquently. Another example is [generating code based on drop-down options](https://cheatlayer.com)—if the code has been verified to work, we can cache it for reliable reuse.

Also, **caching doesn’t only have to occur on-the-fly.** As Redis shared, we
can pre-compute LLM generations offline or asynchronously before serving them.
By serving from a cache, we shift the latency from generation (typically
seconds) to cache lookup (milliseconds). Pre-computing in batch can also help
reduce cost relative to serving in real-time.

While the approaches listed here may not be as flexible as semantically
caching on natural language inputs, I think it provides a good balance between
efficiency and reliability.

## Guardrails: To ensure output quality

In the context of LLMs, guardrails validate the output of LLMs, ensuring that
the output doesn’t just sound good but is also syntactically correct, factual,
and free from harmful content. It also includes guarding against adversarial
input.

### Why guardrails?

First, they help ensure that model outputs are reliable and consistent enough
to use in production. For example, we may require output to be in a specific
JSON schema so that it’s machine-readable, or we need code generated to be
executable. Guardrails can help with such syntactic validation.

Second, they provide an additional layer of safety and maintain quality
control over an LLM’s output. For example, to verify if the content generated
is appropriate for serving, we may want to check that the output isn’t
harmful, verify it for factual accuracy, or ensure coherence with the context
provided.

### More about guardrails

**One approach is to control the model’s responses via prompts.** For example,
Anthropic shared about prompts designed to guide the model toward generating
responses that are [helpful, harmless, and
honest](https://arxiv.org/abs/2204.05862) (HHH). They found that Python fine-
tuning with the HHH prompt led to better performance compared to fine-tuning
with RLHF.

![Example of HHH prompt](/assets/hhh.jpg)

Example of HHH prompt ([source](https://arxiv.org/abs/2204.05862))

**A more common approach is to validate the output.** An example is the
[Guardrails package](https://github.com/ShreyaR/guardrails). It allows users
to add structural, type, and quality requirements on LLM outputs via Pydantic-
style validation. And if the check fails, it can trigger corrective action
such as filtering on the offending output or regenerating another response.

Most of the validation logic is in
[`validators.py`](https://github.com/ShreyaR/guardrails/blob/main/guardrails/validators.py).
It’s interesting to see how they’re implemented. Broadly speaking, its
validators fall into the following categories:

  * Single output value validation: This includes ensuring that the output (i) is one of the predefined choices, (ii) has a length within a certain range, (iii) if numeric, falls within an expected range, and (iv) is a complete sentence.
  * Syntactic checks: This includes ensuring that generated URLs are valid and reachable, and that Python and SQL code is bug-free.
  * Semantic checks: This verifies that the output is aligned with the reference document, or that the extractive summary closely matches the source document. These checks can be done via cosine similarity or fuzzy matching techniques.
  * Safety checks: This ensures that the generated output is free of inappropriate language or that the quality of translated text is high.

Nvidia’s [NeMo-Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) follows
a similar principle but is designed to guide LLM-based conversational systems.
Rather than focusing on syntactic guardrails, it emphasizes semantic ones.
This includes ensuring that the assistant steers clear of politically charged
topics, provides factually correct information, and can detect jailbreaking
attempts.

Thus, NeMo’s approach is somewhat different: Instead of using more
deterministic checks like verifying if a value exists in a list or inspecting
code for syntax errors, NeMo leans heavily on using another LLM to validate
outputs (inspired by [SelfCheckGPT](https://arxiv.org/abs/2303.08896)).

In their example for fact-checking and preventing hallucination, they ask the
LLM itself to check whether the most recent output is consistent with the
given context. To fact-check, the LLM is queried if the response is true based
on the documents retrieved from the knowledge base. To prevent hallucinations,
since there isn’t a knowledge base available, they get the LLM to generate
multiple alternative completions which serve as the context. The underlying
assumption is that if the LLM produces multiple completions that disagree with
one another, the original completion is likely a hallucination.

The moderation example follows a similar approach: The response is screened
for harmful and unethical content via an LLM. Given the nuance of ethics and
harmful content, heuristics and conventional machine learning techniques fall
short. Thus, an LLM is required for a deeper understanding of the intent and
structure of dialogue.

Apart from using guardrails to verify the output of LLMs, we can also
**directly steer the output to adhere to a specific grammar.** An example of
this is Microsoft’s [Guidance](https://github.com/microsoft/guidance). Unlike
Guardrails which [imposes JSON schema via a
prompt](https://github.com/ShreyaR/guardrails/blob/main/guardrails/constants.xml#L14),
Guidance enforces the schema by injecting tokens that make up the structure.

We can think of Guidance as a domain-specific language for LLM interactions
and output. It draws inspiration from [Handlebars](https://handlebarsjs.com),
a popular templating language used in web applications that empowers users to
perform variable interpolation and logical control.

However, Guidance sets itself apart from regular templating languages by
executing linearly. This means it maintains the order of tokens generated.
Thus, by inserting tokens that are part of the structure—instead of relying on
the LLM to generate them correctly—Guidance can dictate the specific output
format. In their examples, they show how to [generate JSON that’s always
valid](https://github.com/microsoft/guidance#guaranteeing-valid-syntax-json-
example-notebook), [generate complex output
formats](https://github.com/microsoft/guidance#rich-output-structure-example-
notebook) with multiple keys, ensure that LLMs [play the right
roles](https://github.com/microsoft/guidance#role-based-chat-model-example-
notebook), and have [agents interact with each
other](https://github.com/microsoft/guidance#agents-notebook).

They also introduced a concept called [token
healing](https://github.com/microsoft/guidance#token-healing-notebook), a
useful feature that helps avoid subtle bugs that occur due to tokenization. In
simple terms, it rewinds the generation by one token before the end of the
prompt and then restricts the first generated token to have a prefix matching
the last token in the prompt. This eliminates the need to fret about token
boundaries when crafting prompts.

### How to apply guardrails?

Though the concept of guardrails for LLMs in industry is still nascent, there
are a handful of immediately useful and practical strategies we can consider.

**Structural guidance:** Apply guidance whenever possible. It provides direct
control over outputs and offers a more precise method to ensure that output
conforms to a specific structure or format.

**Syntactic guardrails:** These include checking if categorical output is
within a set of acceptable choices, or if numeric output is within an expected
range. Also, if we generate SQL, these can verify its free from syntax errors
and also ensure that all columns in the query match the schema. Ditto for
generating code (e.g., Python, JavaScript).

**Content safety guardrails:** These verify that the output has no harmful or
inappropriate content. It can be as simple as checking against the [List of
Dirty, Naughty, Obscene, and Otherwise Bad
Words](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-
Bad-Words) or using [profanity detection](https://pypi.org/project/profanity-
check/) models. (It’s [common to run moderation classifiers on
output](https://twitter.com/goodside/status/1685023251532320768).) More
complex and nuanced output can rely on an LLM evaluator.

**Semantic/factuality guardrails:** These confirm that the output is
semantically relevant to the input. Say we’re generating a two-sentence
summary of a movie based on its synopsis. We can validate if the produced
summary is semantically similar to the output, or have (another) LLM ascertain
if the summary accurately represents the provided synopsis.

**Input guardrails:** These limit the types of input the model will respond
to, helping to mitigate the risk of the model responding to inappropriate or
adversarial prompts which would lead to generating harmful content. For
example, you’ll get an error if you ask Midjourney to generate NSFW content.
This can be as straightforward as comparing against a list of strings or using
a moderation classifier.

![An example of an input guardrail on Midjourney](/assets/input-guardrail.jpg)

An example of an input guardrail on Midjourney

## Defensive UX: To anticipate & handle errors gracefully

Defensive UX is a design strategy that acknowledges that bad things, such as
inaccuracies or hallucinations, can happen during user interactions with
machine learning or LLM-based products. Thus, the intent is to anticipate and
manage these in advance, primarily by guiding user behavior, averting misuse,
and handling errors gracefully.

### Why defensive UX?

Machine learning and LLMs aren’t perfect—they can produce inaccurate output.
Also, they respond differently to the same input over time, such as search
engines displaying varying results due to personalization, or LLMs generating
diverse output on more creative, higher temperature, settings. This can
violate the principle of consistency which advocates for a consistent UI and
predictable behaviors.

Defensive UX can help mitigate the above by providing:

  * **Increased accessibility** : By helping users understand how ML/LLM features work and their limitations, defensive UX makes it more accessible and user-friendly.
  * **Increased trust** : When users see that the feature can handle difficult scenarios gracefully and doesn’t produce harmful output, they’re likely to trust it more.
  * **Better UX** : By designing the system and UX to handle ambiguous situations and errors, defensive UX paves the way for a smoother, more enjoyable user experience.

### More about defensive UX

To learn more about defensive UX, we can look at Human-AI guidelines from
Microsoft, Google, and Apple.

**Microsoft’s[Guidelines for Human-AI
Interaction](https://www.microsoft.com/en-us/research/publication/guidelines-
for-human-ai-interaction/)** is based on a survey of 168 potential guidelines.
These were collected from internal and external industry sources, academic
literature, and public articles. After combining guidelines that were similar,
filtering guidelines that were too vague or too specific or not AI-specific,
and a round of heuristic evaluation, they narrowed it down to 18 guidelines.

![Guidelines for Human-AI interaction across the user journey](/assets/ms-
guidelines.jpg)

Guidelines for Human-AI interaction across the user journey
([source](https://www.microsoft.com/en-us/research/project/guidelines-for-
human-ai-interaction/))

These guidelines follow a certain style: Each one is a succinct action rule of
3 - 10 words, beginning with a verb. Each rule is accompanied by a one-liner
that addresses potential ambiguities. They are organized based on their likely
application during user interaction:

  * Initially: Make clear what the system can do (G1), make clear how well the system can do what it can do (G2)
  * During interaction: Time services based on context (G3), mitigate social biases (G6)
  * When wrong: Support efficient dismissal (G8), support efficient correction (G9)
  * Over time: Learn from user behavior (G13), provide global controls (G17)

**Google’s[People + AI Guidebook](https://pair.withgoogle.com/guidebook/)** is
rooted in data and insights drawn from Google’s product team and academic
research. In contrast to Microsoft’s guidelines which are organized around the
user, Google organizes its guidelines into concepts that a developer needs to
keep in mind.

There are 23 patterns grouped around common questions that come up during the
product development process, including:

  * How do I get started with human-centered AI: Determine if the AI adds value, invest early in good data practices (e.g., evals)
  * How do I onboard users to new AI features: Make it safe to explore, anchor on familiarity, automate in phases
  * How do I help users build trust in my product: Set the right expectations, be transparent, automate more when the risk is low.

**Apple’s[Human Interface Guidelines for Machine
Learning](https://developer.apple.com/design/human-interface-
guidelines/machine-learning)** differs from the bottom-up approach of academic
literature and user studies. Instead, its primary source is practitioner
knowledge and experience. Thus, it doesn’t include many references or data
points, but instead focuses on Apple’s longstanding design principles. This
results in a unique perspective that distinguishes it from the other two
guidelines.

The document focuses on how Apple’s design principles can be applied to ML-
infused products, emphasizing aspects of UI rather than model functionality.
It starts by asking developers to consider the role of ML in their app and
work backwards from the user experience. This includes questions such as
whether ML is:

  * Critical or complementary: For example, Face ID cannot work without ML but the keyboard can still work without QuickType.
  * Proactive or reactive: Siri Suggestions are proactive while autocorrect is reactive.
  * Dynamic or static: Recommendations are dynamic while object detection in Photos only improves with each iOS release.

It then delves into several patterns, split into inputs and outputs of a
system. Inputs focus on explicit feedback, implicit feedback, calibration, and
corrections. This section guides the design for how AI products request and
process user data and interactions. Outputs focus on mistakes, multiple
options, confidence, attribution, and limitations. The intent is to ensure the
model’s output is presented in a comprehensible and useful manner.

The differences between the three guidelines are insightful. Google has more
emphasis on considerations for training data and model development, likely due
to its engineering-driven culture. Microsoft has more focus on mental models,
likely an artifact of the HCI academic study. Lastly, Apple’s approach centers
around providing a seamless UX, a focus likely influenced by its cultural
values and principles.

### How to apply defensive UX?

Here are some patterns based on the guidelines above. (Disclaimer: I’m not a
designer.)

**Set the right expectations.** This principle is consistent across all three
guidelines:

  * Microsoft: Make clear how well the system can do what it can do (help the user understand how often the AI system may make mistakes)
  * Google: Set the right expectations (be transparent with your users about what your AI-powered product can and cannot do)
  * Apple: Help people establish realistic expectations (describe the limitation in marketing material or within the feature’s context)

This can be as simple as adding a brief disclaimer above AI-generated results,
like those of Bard, or highlighting our app’s limitations on its landing page,
like how ChatGPT does it.

![Example of a disclaimer on Google Bard results \(Note: The code provided
will not work.\)](/assets/bard-disclaimer.png)

Example of a disclaimer on Google Bard results (Note: `nrows` is not a valid
argument.)

By being transparent about our product’s capabilities and limitations, we help
users calibrate their expectations about its functionality and output. While
this may cause users to trust it less in the short run, it helps foster trust
in the long run—users are less likely to overestimate our product and
subsequently face disappointment.

**Enable efficient dismissal.** This is explicitly mentioned as Microsoft’s
Guideline 8: Support efficient dismissal (make it easy to dismiss or ignore
undesired AI system services).

For example, if a user is navigating our site and a chatbot pops up asking if
they need help, it should be easy for the user to dismiss the chatbot. This
ensures the chatbot doesn’t get in the way, especially on devices with smaller
screens. Similarly, GitHub Copilot allows users to conveniently ignore its
code suggestions by simply continuing to type. While this may reduce usage of
the AI feature in the short term, it prevents it from becoming a nuisance and
potentially reducing customer satisfaction in the long term.

**Provide attribution.** This is listed in all three guidelines:

  * Microsoft: Make clear why the system did what it did (enable the user to access an explanation of why the AI system behaved as it did)
  * Google: Add context from human sources (help users appraise your recommendations with input from 3rd-party sources)
  * Apple: Consider using attributions to help people distinguish among results

Citations are becoming an increasingly common design element. Take BingChat
for example. When we make a query, it includes citations, usually from
reputable sources, in its responses. This not only shows where the information
came from, but also allows users to assess the quality of the sources.
Similarly, imagine we’re using an LLM to explain why a user might like a
product. Alongside the LLM-generated explanation, we could include a quote
from an actual review or mention the product rating.

Context from experts and the community also enhances user trust. For example,
if a user is seeking recommendations for a hiking trail, mentioning that a
suggested trail comes highly recommended by the relevant community can go a
long way. It not only adds value to the recommendation but also helps users
calibrate trust through the human connection.

![Example of attribution via social proof](/assets/social-proof.jpg)

Example of attribution via social proof
([source](https://pair.withgoogle.com/guidebook/patterns))

Finally, Apple’s guidelines include popular attributions such as “Because
you’ve read non-fiction”, “New books by authors you’ve read”. These
descriptors not only personalize the experience but also provide context,
enhancing user understanding and trust.

**Anchor on familiarity.** When introducing users to a new AI product or
feature, it helps to guide them with familiar UX patterns and features. This
makes it easier for users to focus on the main task and start to earn customer
trust in our new product. Resist the temptation to showcase new and “magical”
features via exotic UI elements.

Along a similar vein, chat-based features are becoming more common due to
ChatGPT’s growing popularity. For example, chat with your docs, chat to query
your data, chat to buy groceries. However, I [question whether chat is the
right UX](/writing/llm-ux/) for most user experiences—it just takes too much
effort relative to the familiar UX of clicking on text and images.

Furthermore, increasing user effort leads to higher expectations that are
harder to meet. Netflix shared that users have [higher expectations for
recommendations](https://slideslive.com/38934788/a-human-perspective-on-
algorithmic-similarity?ref=folder-59726) that result from explicit actions
such as search. In general, the more effort a user puts in (e.g., chat,
search), the higher the expectations they have. Contrast this with lower-
effort interactions such as scrolling over recommendations slates or clicking
on a product.

Thus, while chat offers more flexibility, it also demands more user effort.
Moreover, using a chat box is less intuitive as it lacks signifiers on how
users can adjust the output. Overall, I think that sticking with a familiar
and constrained UI makes it easier for users to navigate our product; chat
should only be considered as a secondary or tertiary option.

## Collect user feedback: To build our data flywheel

Gathering user feedback allows us to learn their preferences. Specific to LLM
products, user feedback contributes to building evals, fine-tuning, and
guardrails. If we think about it, data—such as corpus for pre-training,
expert-crafted demonstrations, human preferences for reward modeling—is one of
the few moats for LLM products. Thus, we want to be deliberately thinking
about collecting user feedback when designing our UX.

Feedback can be explicit or implicit. Explicit feedback is information users
provide in response to a request by our product; implicit feedback is
information we learn from user interactions without needing users to
deliberately provide feedback.

### Why collect user feedback

User feedback **helps our models improve**. By learning what users like,
dislike, or complain about, we can improve our models to better meet their
needs. It also allows us to **adapt to individual preferences**.
Recommendation systems are a prime example. As users interact with items, we
learn what they like and dislike and better cater to their tastes over time.

In addition, the feedback loop helps us **evaluate our system’s overall
performance**. While evals can help us measure model/system performance, user
feedback offers a concrete measure of user satisfaction and product
effectiveness.

### How to collect user feedback

**Make it easy for users to provide feedback.** This is echoed across all
three guidelines:

  * Microsoft: Encourage granular feedback (enable the user to provide feedback indicating their preferences during regular interaction with the AI system)
  * Google: Let users give feedback (give users the opportunity for real-time teaching, feedback, and error correction)
  * Apple: Provide actionable information your app can use to improve the content and experience it presents to people

ChatGPT is one such example. Users can indicate thumbs up/down on responses,
or choose to regenerate a response if it’s really bad or unhelpful. This is
useful feedback on human preferences which can then be used to fine-tune LLMs.

Midjourney is another good example. After images are generated, users can
generate a new set of images (negative feedback), tweak an image by asking for
a variation (positive feedback), or upscale and download the image (strong
positive feedback). This enables Midjourney to gather rich comparison data on
the outputs generated.

![>Example of collecting user feedback as part of the
UX](/assets/midjourney.jpg)

Example of collecting user feedback as part of the UX

**Consider implicit feedback too.** Implicit feedback is information that
arises as users interact with our product. Unlike the specific responses we
get from explicit feedback, implicit feedback can provide a wide range of data
on user behavior and preferences.

Copilot-like assistants are a prime example. Users indicate whether a
suggestion was helpful by either wholly accepting it (strong positive
feedback), accepting and making minor tweaks (positive feedback), or ignoring
it (neutral/negative feedback). Alternatively, they may update the comment
that led to the generated code, suggesting that the initial code generation
didn’t meet their needs.

Chatbots, such as ChatGPT and BingChat, are another example. How has daily
usage changed over time? If the product is sticky, it suggests that users like
it. Also, how long is the average conversation? This can be tricky to
interpret: Is a longer conversation better because the conversation was
engaging and fruitful? Or is it worse because it took the user longer to get
what they needed?

## Other patterns common in machine learning

Apart from the seven patterns above, there are other patterns in machine
learning that are also relevant to LLM systems and products. They include:

  * [Data flywheel](/writing/more-patterns/#data-flywheel-to-continuously-improve--build-a-moat): Continuous data collection improves the model and leads to a better user experience. This, in turn, promotes more usage which provides more data to further evaluate and fine-tune models, creating a virtuous cycle.
  * [Cascade](/writing/more-patterns/#cascade-to-split-a-problem-into-smaller-problems): Rather than assigning a single, complex task to the LLM, we can simplify and break it down so it only has to handle tasks it excels at, such as reasoning or communicating eloquently. RAG is an example of this. Instead of relying on the LLM to retrieve and rank items based on its internal knowledge, we can augment LLMs with external knowledge and focus on applying the LLM’s reasoning abilities.
  * [Monitoring](/writing/practical-guide-to-maintaining-machine-learning/#monitor-models-for-misbehaviour-when-retraining): This helps demonstrate the value added by the AI system, or the lack of it. Someone shared an anecdote of running an LLM-based customer support solution in prod for two weeks before discontinuing it—an A/B test showed that losses were 12x more when using an LLM as a substitute for their support team!

(Read more about design patterns for [machine learning code](/writing/design-
patterns/) and [systems](/writing/more-patterns/).)

Also, here’s what others said:

> Separation of concerns/task decomposition- having distinct prompts for
> distinct subtasks and chaining them together helps w attention and
> reliability (hurts latency). We were having trouble specifying a rigid
> output structure AND variable response content so we split up the tasks —
> [Erick Enriquez](https://twitter.com/generick_ez/status/1681153738822516736)

> A few others that will be needed: role based access control: who can access
> what; security: if I’m using a DB with an LLM, how do I ensure that I have
> the right security guards —
> [Krishna](https://twitter.com/ntkris/status/16812092400299991050)

> Consistent output format: setting outputs to a standardized format such as
> JSON; Tool augmentation: offload tasks to more specialised, proven, reliable
> models — [Paul Tune](https://twitter.com/ptuls/status/1681284873741561857)

> Security: mitigate cache poisoning, input validation, mitigate prompt
> injection, training data provenance, output with non-vulnerable code,
> mitigate malicious input aimed at influencing requests used by tools (AI
> Agent), mitigate denial of service (stress test llm), to name a few :) —
> [Anderson
> Darario](https://www.linkedin.com/feed/update/urn:li:activity:7087089908229558272?commentUrn=urn%3Ali%3Acomment%3A%28activity%3A7087089908229558272%2C7087224131292684288%29)

> Another ux/ui related: incentivize users to provide feedback on generated
> answers (implicit or explicit). Implicit could be sth like copilot’s ghost
> text style, if accepted with TAB, meaning positive feedback etc. — [Wen
> Yang](https://www.linkedin.com/feed/update/urn:li:activity:7087089908229558272?commentUrn=urn%3Ali%3Acomment%3A%28activity%3A7087089908229558272%2C7087149792660750336%29)

> Great list. I would add consistency checks like self-consistency sampling,
> chaining and decomposition of tasks, and the emsembling of multiple model
> outputs. Applying each of these almost daily. [Dan
> White](https://www.threads.net/@dwhitena/post/Cu3BBaJtoyj/?igshid=OGQ5ZDc2ODk2ZA==)

> Guardrails is super relevant for building analytics tools where llm is a
> translator from natural to programming language —
> [m_voitko](https://www.threads.net/@m_voitko/post/Cu1b4liNwCS/?igshid=OGQ5ZDc2ODk2ZA==)

## Conclusion

This is the longest post I’ve written by far. If you’re still with me, thank
you! I hope you found reading about these patterns helpful, and that the 2x2
below makes sense.

![LLM patterns across the axis of data to user, and defensive to
offensive.](/assets/llm-patterns.png)

LLM patterns across the axis of data to user, and defensive to offensive.

We’re still so early on the journey towards building LLM-based systems and
products. Are there any other key patterns or resources? What have you found
useful or not useful? I’d love to hear your experience. **Please[reach
out!](https://twitter.com/eugeneyan)**

## References

Hendrycks, Dan, et al. [“Measuring massive multitask language
understanding.”](https://arxiv.org/abs/2009.03300) arXiv preprint
arXiv:2009.03300 (2020).

Gao, Leo, et al. [“A Framework for Few-Shot Language Model
Evaluation.”](https://github.com/EleutherAI/lm-evaluation-harness) v0.0.1,
Zenodo, (2021), doi:10.5281/zenodo.5371628.

Liang, Percy, et al. [“Holistic evaluation of language
models.”](https://arxiv.org/abs/2211.09110) arXiv preprint arXiv:2211.09110
(2022).

Dubois, Yann, et al. [“AlpacaFarm: A Simulation Framework for Methods That
Learn from Human Feedback.”](https://github.com/tatsu-lab/alpaca_eval) (2023)

Papineni, Kishore, et al. [“Bleu: a method for automatic evaluation of machine
translation.”](https://dl.acm.org/doi/10.3115/1073083.1073135) Proceedings of
the 40th annual meeting of the Association for Computational Linguistics.
2002.

Lin, Chin-Yew. [“Rouge: A package for automatic evaluation of
summaries.”](https://aclanthology.org/W04-1013/) Text summarization branches
out. 2004.

Zhang, Tianyi, et al. [“Bertscore: Evaluating text generation with
bert.”](https://arxiv.org/abs/1904.09675) arXiv preprint arXiv:1904.09675
(2019).

Zhao, Wei, et al. [“MoverScore: Text generation evaluating with contextualized
embeddings and earth mover distance.”](https://arxiv.org/abs/1909.02622) arXiv
preprint arXiv:1909.02622 (2019).

Sai, Ananya B., Akash Kumar Mohankumar, and Mitesh M. Khapra. [“A survey of
evaluation metrics used for NLG systems.”](https://arxiv.org/abs/2008.12009)
ACM Computing Surveys (CSUR) 55.2 (2022): 1-39.

Grusky, Max. [“Rogue Scores.”](https://aclanthology.org/2023.acl-long.107/)
Proceedings of the 61st Annual Meeting of the Association for Computational
Linguistics (Volume 1: Long Papers). 2023.

Liu, Yang, et al. [“Gpteval: Nlg evaluation using gpt-4 with better human
alignment.”](https://arxiv.org/abs/2303.16634) arXiv preprint arXiv:2303.16634
(2023).

Fourrier, Clémentine, et al. [“What’s going on with the Open LLM
Leaderboard?”](https://huggingface.co/blog/evaluating-mmlu-leaderboard#whats-
going-on-with-the-open-llm-leaderboard) (2023).

Zheng, Lianmin, et al. [“Judging LLM-as-a-judge with MT-Bench and Chatbot
Arena.”](https://arxiv.org/abs/2306.05685) arXiv preprint arXiv:2306.05685
(2023).

Dettmers, Tim, et al. [“Qlora: Efficient finetuning of quantized
llms.”](https://arxiv.org/abs/2305.14314) arXiv preprint arXiv:2305.14314
(2023).

Swyx et al. [MPT-7B and The Beginning of
Context=Infinity](https://www.latent.space/p/mosaic-mpt-7b#details) (2023).

Fradin, Michelle, Reeder, Lauren [“The New Language Model
Stack”](https://www.sequoiacap.com/article/llm-stack-perspective/) (2023).

Radford, Alec, et al. [“Learning transferable visual models from natural
language supervision.”](https://arxiv.org/abs/2103.00020) International
conference on machine learning. PMLR, 2021.

Yan, Ziyou. [“Search: Query Matching via Lexical, Graph, and Embedding
Methods.”](https://eugeneyan.com/writing/search-query-matching/)
eugeneyan.com, (2021).

Petroni, Fabio, et al. [“How context affects language models’ factual
predictions.”](https://arxiv.org/abs/2005.04611) arXiv preprint
arXiv:2005.04611 (2020).

Karpukhin, Vladimir, et al. [“Dense passage retrieval for open-domain question
answering.”](https://arxiv.org/abs/2004.04906) arXiv preprint arXiv:2004.04906
(2020).

Lewis, Patrick, et al. [“Retrieval-augmented generation for knowledge-
intensive nlp tasks.”](https://arxiv.org/abs/2005.11401) Advances in Neural
Information Processing Systems 33 (2020): 9459-9474.

Izacard, Gautier, and Edouard Grave. [“Leveraging passage retrieval with
generative models for open domain question
answering.”](https://arxiv.org/abs/2007.01282) arXiv preprint arXiv:2007.01282
(2020).

Borgeaud, Sebastian, et al. [“Improving language models by retrieving from
trillions of tokens.”](https://arxiv.org/abs/2112.04426) International
conference on machine learning. PMLR, (2022).

Lazaridou, Angeliki, et al. [“Internet-augmented language models through few-
shot prompting for open-domain question
answering.”](https://arxiv.org/abs/2203.05115) arXiv preprint arXiv:2203.05115
(2022).

Wang, Yue, et al. [“Codet5+: Open code large language models for code
understanding and generation.”](https://arxiv.org/abs/2305.07922) arXiv
preprint arXiv:2305.07922 (2023).

Gao, Luyu, et al. [“Precise zero-shot dense retrieval without relevance
labels.”](https://arxiv.org/abs/2212.10496) arXiv preprint arXiv:2212.10496
(2022).

Yan, Ziyou. [“Obsidian-Copilot: An Assistant for Writing &
Reflecting.”](https://eugeneyan.com/writing/obsidian-copilot/) eugeneyan.com,
(2023).

Bojanowski, Piotr, et al. [“Enriching word vectors with subword
information.”](https://arxiv.org/abs/1607.04606) Transactions of the
association for computational linguistics 5 (2017): 135-146.

Reimers, Nils, and Iryna Gurevych. [“Making Monolingual Sentence Embeddings
Multilingual Using Knowledge Distillation.”](https://arxiv.org/abs/2004.09813)
Proceedings of the 2020 Conference on Empirical Methods in Natural Language
Processing, Association for Computational Linguistics, (2020).

Wang, Liang, et al. [“Text embeddings by weakly-supervised contrastive pre-
training.”](https://arxiv.org/abs/2212.03533) arXiv preprint arXiv:2212.03533
(2022).

Su, Hongjin, et al. [“One embedder, any task: Instruction-finetuned text
embeddings.”](https://arxiv.org/abs/2212.09741) arXiv preprint
arXiv:2212.09741 (2022).

Johnson, Jeff, et al. [“Billion-Scale Similarity Search with
GPUs.”](https://arxiv.org/abs/1702.08734) IEEE Transactions on Big Data, vol.
7, no. 3, IEEE, 2019, pp. 535–47.

Malkov, Yu A., and Dmitry A. Yashunin. [“Efficient and Robust Approximate
Nearest Neighbor Search Using Hierarchical Navigable Small World
Graphs.”](https://arxiv.org/abs/1603.09320) IEEE Transactions on Pattern
Analysis and Machine Intelligence, vol. 42, no. 4, IEEE, 2018, pp. 824–36.

Guo, Ruiqi, et al. [“Accelerating Large-Scale Inference with Anisotropic
Vector Quantization.”](https://arxiv.org/abs/1908.10396.) International
Conference on Machine Learning, (2020)

Ouyang, Long, et al. [“Training language models to follow instructions with
human feedback.”](https://arxiv.org/abs/2203.02155) Advances in Neural
Information Processing Systems 35 (2022): 27730-27744.

Howard, Jeremy, and Sebastian Ruder. [“Universal language model fine-tuning
for text classification.”](https://arxiv.org/abs/1801.06146) arXiv preprint
arXiv:1801.06146 (2018).

Devlin, Jacob, et al. [“Bert: Pre-training of deep bidirectional transformers
for language understanding.”](https://arxiv.org/abs/1810.04805) arXiv preprint
arXiv:1810.04805 (2018).

Radford, Alec, et al. [“Improving language understanding with unsupervised
learning.”](https://openai.com/research/language-unsupervised) (2018).

Raffel, Colin, et al. [“Exploring the limits of transfer learning with a
unified text-to-text transformer.”](https://arxiv.org/abs/1910.10683) The
Journal of Machine Learning Research 21.1 (2020): 5485-5551.

Lester, Brian, Rami Al-Rfou, and Noah Constant. [“The power of scale for
parameter-efficient prompt tuning.”](https://arxiv.org/abs/2104.08691) arXiv
preprint arXiv:2104.08691 (2021).

Li, Xiang Lisa, and Percy Liang. [“Prefix-tuning: Optimizing continuous
prompts for generation.”](https://arxiv.org/abs/2101.00190) arXiv preprint
arXiv:2101.00190 (2021).

Houlsby, Neil, et al. [“Parameter-efficient transfer learning for
NLP.”](https://arxiv.org/abs/1902.00751) International Conference on Machine
Learning. PMLR, 2019.

Hu, Edward J., et al. [“Lora: Low-rank adaptation of large language
models.”](https://arxiv.org/abs/2106.09685) arXiv preprint arXiv:2106.09685
(2021).

Dettmers, Tim, et al. [“Qlora: Efficient finetuning of quantized
llms.”](https://arxiv.org/abs/2305.14314) arXiv preprint arXiv:2305.14314
(2023).

Williams, Adina, et al. [“A Broad-Coverage Challenge Corpus for Sentence
Understanding through Inference.”](https://cims.nyu.edu/~sbowman/multinli/)
Proceedings of the 2018 Conference of the North American Chapter of the
Association for Computational Linguistics: Human Language Technologies, Volume
1 (Long Papers), Association for Computational Linguistics, (2018).

[GPTCache](https://github.com/zilliztech/GPTCache) (2023).

Bai, Yuntao, et al. [“Training a helpful and harmless assistant with
reinforcement learning from human
feedback.”](https://arxiv.org/abs/2204.05862) arXiv preprint arXiv:2204.05862
(2022).

[Guardrails](https://github.com/ShreyaR/guardrails) (2023)

[NeMo-Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) (2023)

Manakul, Potsawee, Adian Liusie, and Mark JF Gales. [“Selfcheckgpt: Zero-
resource black-box hallucination detection for generative large language
models.”](https://arxiv.org/abs/2303.08896) arXiv preprint arXiv:2303.08896
(2023).

[Guidance](https://github.com/microsoft/guidance) (2023).

Amershi, Saleema, et al. [“Guidelines for human-AI
interaction.”](https://www.microsoft.com/en-
us/research/publication/guidelines-for-human-ai-interaction/) Proceedings of
the 2019 chi conference on human factors in computing systems. 2019.

[People + AI Guidebook](https://pair.withgoogle.com/guidebook/) (2023).

[Human Interface Guidelines for Machine
Learning](https://developer.apple.com/design/human-interface-
guidelines/machine-learning) (2023).

Schendel, Zachary A., Faraz Farzin, and Siddhi Sundar. [“A Human Perspective
on Algorithmic Similarity.”](https://slideslive.com/38934788/a-human-
perspective-on-algorithmic-similarity?ref=folder-59726) Proceedings of the
14th ACM Conference on Recommender Systems. 2020.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jul 2023). Patterns for Building LLM-based Systems & Products.
> eugeneyan.com. https://eugeneyan.com/writing/llm-patterns/.

or

    
    
    @article{yan2023llm-patterns,
      title   = {Patterns for Building LLM-based Systems & Products},
      author  = {Yan, Ziyou},
      journal = {eugeneyan.com},
      year    = {2023},
      month   = {Jul},
      url     = {https://eugeneyan.com/writing/llm-patterns/}
    }

  
Share on:

![](/assets/icon-twitter.svg)

![](/assets/icon-linkedin.svg)

![](/assets/icon-facebook.svg)

![](/assets/icon-mail.svg)

  
Browse related tags: [ [llm](/tag/llm/) [engineering](/tag/engineering/)
[production](/tag/production/) [🔥](/tag/🔥/) ]

[ ![](/assets/icon-search.svg)Search](/search/ "Search")

[« Obsidian-Copilot: An Assistant for Writing & Reflecting](/writing/obsidian-
copilot/) [How to Match LLM Patterns to Problems »](/writing/llm-problems/)

* * *

Join **6,800+** readers getting updates on machine learning, RecSys, LLMs, and
engineering.

Get email updates

* * *

  * ![](/assets/icon-twitter.svg) [Twitter](https://twitter.com/eugeneyan "Twitter")
  * ![](/assets/icon-linkedin.svg) [LinkedIn](https://www.linkedin.com/in/eugeneyan/ "Linkedin")
  * ![](/assets/icon-threads.svg) [Threads](https://www.threads.net/@eugeneyan "Threads")
  * ![](/assets/icon-github.svg) [GitHub](https://github.com/eugeneyan/ "GitHub")

Eugene Yan designs, builds, and operates machine learning systems that serve
customers at scale. He's currently a Senior Applied Scientist at Amazon.
Previously, he led machine learning at Lazada (acquired by Alibaba) and a
Healthtech Series A. He [writes](/writing/) & [speaks](/speaking/) about
machine learning, recommenders, LLMs, and engineering at
[eugeneyan.com](https://eugeneyan.com/) and
[ApplyingML.com](https://applyingml.com/).

© Eugene Yan 2015 - 2024 • [Feedback](/site-feedback/) • [RSS](/rss/)



```

## Nodes¶
In [ ]:
Copied!
```
orig_nodes = node_parser.get_nodes_from_documents(docs)

```

orig_nodes = node_parser.get_nodes_from_documents(docs)
In [ ]:
Copied!
```
print(orig_nodes[20:28][3].get_content(metadata_mode="all"))

```

print(orig_nodes[20:28][3].get_content(metadata_mode="all"))
```
because evals were often conducted with untested, incorrect
ROUGE implementations.

![Dimensions of model evaluations with ROUGE](/assets/rogue-scores.jpg)

Dimensions of model evaluations with ROUGE
([source](https://aclanthology.org/2023.acl-long.107/))

And even with recent benchmarks such as MMLU, **the same model can get
significantly different scores based on the eval implementation**.
[Huggingface compared the original MMLU
implementation](https://huggingface.co/blog/evaluating-mmlu-leaderboard) with
the HELM and EleutherAI implementations and found that the same example could
have different prompts across various providers.

![Different prompts for the same question across MMLU
implementations](/assets/mmlu-prompt.jpg)

Different prompts for the same question across MMLU implementations
([source](https://huggingface.co/blog/evaluating-mmlu-leaderboard))

Furthermore, the evaluation approach differed across all three benchmarks:

  * Original MMLU: Compares predicted probabilities on the answers only (A, B, C, D)
  * HELM: Uses the next token probabilities from the model and picks the token with the

```

## Question Extractor on Nodes¶
In [ ]:
Copied!
```
nodes_1 = node_parser.get_nodes_from_documents(docs)[20:28]
nodes_1 = question_extractor(nodes_1)

```

nodes_1 = node_parser.get_nodes_from_documents(docs)[20:28] nodes_1 = question_extractor(nodes_1)
```
100%|██████████| 8/8 [00:03<00:00,  2.04it/s]

```

In [ ]:
Copied!
```
print(nodes_1[3].get_content(metadata_mode="all"))

```

print(nodes_1[3].get_content(metadata_mode="all"))
```
[Excerpt from document]
questions_this_excerpt_can_answer: 1. How do different implementations of the MMLU benchmark affect the scores of the same model?
2. What are the differences in evaluation approaches between the original MMLU benchmark, HELM, and EleutherAI implementations?
3. How do various providers differ in the prompts they use for evaluating models in the MMLU benchmark?
Excerpt:
-----
because evals were often conducted with untested, incorrect
ROUGE implementations.

![Dimensions of model evaluations with ROUGE](/assets/rogue-scores.jpg)

Dimensions of model evaluations with ROUGE
([source](https://aclanthology.org/2023.acl-long.107/))

And even with recent benchmarks such as MMLU, **the same model can get
significantly different scores based on the eval implementation**.
[Huggingface compared the original MMLU
implementation](https://huggingface.co/blog/evaluating-mmlu-leaderboard) with
the HELM and EleutherAI implementations and found that the same example could
have different prompts across various providers.

![Different prompts for the same question across MMLU
implementations](/assets/mmlu-prompt.jpg)

Different prompts for the same question across MMLU implementations
([source](https://huggingface.co/blog/evaluating-mmlu-leaderboard))

Furthermore, the evaluation approach differed across all three benchmarks:

  * Original MMLU: Compares predicted probabilities on the answers only (A, B, C, D)
  * HELM: Uses the next token probabilities from the model and picks the token with the
-----

```

## Build Indices¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.response.notebook_utils import (
    display_source_node,
    display_response,
)

```

from llama_index.core import VectorStoreIndex from llama_index.core.response.notebook_utils import ( display_source_node, display_response, )
In [ ]:
Copied!
```
index0 = VectorStoreIndex(orig_nodes)
index1 = VectorStoreIndex(orig_nodes[:20] + nodes_1 + orig_nodes[28:])

```

index0 = VectorStoreIndex(orig_nodes) index1 = VectorStoreIndex(orig_nodes[:20] + nodes_1 + orig_nodes[28:])
## Query Engines¶
In [ ]:
Copied!
```
query_engine0 = index0.as_query_engine(similarity_top_k=1)
query_engine1 = index1.as_query_engine(similarity_top_k=1)

```

query_engine0 = index0.as_query_engine(similarity_top_k=1) query_engine1 = index1.as_query_engine(similarity_top_k=1)
## Querying¶
In [ ]:
Copied!
```
query_str = (
    "Can you describe metrics for evaluating text generation quality, compare"
    " them, and tell me about their downsides"
)

response0 = query_engine0.query(query_str)
response1 = query_engine1.query(query_str)

```

query_str = ( "Can you describe metrics for evaluating text generation quality, compare" " them, and tell me about their downsides" ) response0 = query_engine0.query(query_str) response1 = query_engine1.query(query_str)
In [ ]:
Copied!
```
display_response(
    response0, source_length=1000, show_source=True, show_source_metadata=True
)

```

display_response( response0, source_length=1000, show_source=True, show_source_metadata=True )
**`Final Response:`**Metrics for evaluating text generation quality can be categorized as context-dependent or context-free. Context-dependent metrics consider the context of the task and may need adjustments for different tasks. On the other hand, context-free metrics do not consider task-specific context and are easier to apply across various tasks.
Some commonly used metrics for evaluating text generation quality include BLEU, ROUGE, BERTScore, and MoverScore.
  * **BLEU (Bilingual Evaluation Understudy)** is a precision-based metric that compares n-grams in the generated output with those in the reference.
  * **ROUGE (Recall-Oriented Understudy for Gisting Evaluation)** evaluates the overlap between the generated output and reference summaries.
  * **BERTScore** leverages contextual embeddings to measure the similarity between the generated output and reference.
  * **MoverScore** considers the semantic similarity between the generated output and reference using Earth Mover's Distance.


Each of these metrics has its own strengths and weaknesses. For example, BLEU may not capture the overall fluency and coherence of the generated text, while ROUGE may not consider the semantic meaning adequately. BERTScore and MoverScore, on the other hand, may require pre-trained models and can be computationally expensive. It's important to consider the specific requirements of the task when selecting an appropriate evaluation metric.
* * *
**`Source Node 1/1`**
**Node ID:** 4edc4466-e9ae-47ae-b0ee-8a8ac27a0378  
**Similarity:** 0.8381672789063448  
**Text:** GPT-4) prefers the output of one model over a reference model. Metrics include win rate, bias, latency, price, variance, etc. Validated to have high agreement with 20k human annotations.
We can group metrics into two categories: context-dependent or context-free.
  * **Context-dependent** : These take context into account. They’re often proposed for a specific task; repurposing them for other tasks will require some adjustment.
  * **Context-free** : These aren’t tied to the context when evaluating generated output; they only compare the output with the provided gold references. As they’re task agnostic, they’re easier to apply to a wide variety of tasks.


To get a better sense of these metrics (and their potential shortfalls), we’ll explore a few of the commonly used metrics such as BLEU, ROUGE, BERTScore, and MoverScore.
**BLEU (Bilingual Evaluation Understudy)** is a precision-based metric: It counts the number of n-grams in th...  
**Metadata:** {}  

In [ ]:
Copied!
```
display_response(
    response1, source_length=1000, show_source=True, show_source_metadata=True
)

```

display_response( response1, source_length=1000, show_source=True, show_source_metadata=True )
**`Final Response:`**Metrics for evaluating text generation quality include BLEU and ROUGE. These metrics are commonly used but have limitations. BLEU and ROUGE have shown poor correlation with human judgments in terms of fluency and adequacy. They also exhibit low correlation with tasks that require creativity and diversity in text generation. Additionally, exact match metrics like BLEU and ROUGE are not suitable for tasks such as abstractive summarization or dialogue in text generation due to their reliance on n-gram overlap, which may not capture the nuances of these tasks effectively.
* * *
**`Source Node 1/1`**
**Node ID:** 52856a1d-be29-494a-84be-e8db8a736675  
**Similarity:** 0.8459422950143721  
**Text:** finds the minimum effort to transform one text into another. The idea is to measure the distance that words would have to move to convert one sequence to another.
However, there are several pitfalls to using these conventional benchmarks and metrics.
First, there’s **poor correlation between these metrics and human judgments.** BLEU, ROUGE, and others have had negative correlation with how humans evaluate fluency. They also showed moderate to less correlation with human adequacy scores. In particular, BLEU and ROUGE have low correlation with tasks that require creativity and diversity.
Second, these metrics often have **poor adaptability to a wider variety of tasks**. Adopting a metric proposed for one task to another is not always prudent. For example, exact match metrics such as BLEU and ROUGE are a poor fit for tasks like abstractive summarization or dialogue. Since they’re based on n-gram overlap between ...  
**Metadata:** {'questions_this_excerpt_can_answer': '1. How do conventional benchmarks and metrics for measuring text transformation performance compare to human judgments in terms of fluency and adequacy?\n2. What is the correlation between metrics like BLEU and ROUGE and tasks that require creativity and diversity in text generation?\n3. Why are exact match metrics like BLEU and ROUGE not suitable for tasks like abstractive summarization or dialogue in text generation?'}  

## Extract Metadata Using PydanticProgramExtractor¶
PydanticProgramExtractor enables extracting an entire Pydantic object using an LLM.
This approach allows for extracting multiple entities in a single LLM call, offering an advantage over using a single metadata extractor.
In [ ]:
Copied!
```
from pydantic import BaseModel, Field
from typing import List

```

from pydantic import BaseModel, Field from typing import List
### Setup the Pydantic Model¶¶
Here we define a basic structured schema that we want to extract. It contains:
Entities: unique entities in a text chunk Summary: a concise summary of the text chunk
In [ ]:
Copied!
```
class NodeMetadata(BaseModel):
    """Node metadata."""

    entities: List[str] = Field(
        ..., description="Unique entities in this text chunk."
    )
    summary: str = Field(
        ..., description="A concise summary of this text chunk."
    )

```

class NodeMetadata(BaseModel): """Node metadata.""" entities: List[str] = Field( ..., description="Unique entities in this text chunk." ) summary: str = Field( ..., description="A concise summary of this text chunk." )
### Setup the Extractor¶¶
In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core.extractors import PydanticProgramExtractor

EXTRACT_TEMPLATE_STR = """\
Here is the content of the section:
----------------
{context_str}
----------------
Given the contextual information, extract out a {class_name} object.\
"""

openai_program = OpenAIPydanticProgram.from_defaults(
    output_cls=NodeMetadata,
    prompt_template_str="{input}",
    extract_template_str=EXTRACT_TEMPLATE_STR,
)

metadata_extractor = PydanticProgramExtractor(
    program=openai_program, input_key="input", show_progress=True
)

```

from llama_index.program.openai import OpenAIPydanticProgram from llama_index.core.extractors import PydanticProgramExtractor EXTRACT_TEMPLATE_STR = """\ Here is the content of the section: ---------------- {context_str} ---------------- Given the contextual information, extract out a {class_name} object.\ """ openai_program = OpenAIPydanticProgram.from_defaults( output_cls=NodeMetadata, prompt_template_str="{input}", extract_template_str=EXTRACT_TEMPLATE_STR, ) metadata_extractor = PydanticProgramExtractor( program=openai_program, input_key="input", show_progress=True )
### Extract metadata from the node¶
In [ ]:
Copied!
```
extract_metadata = metadata_extractor.extract(orig_nodes[0:1])

```

extract_metadata = metadata_extractor.extract(orig_nodes[0:1])
```
100%|██████████| 1/1 [00:01<00:00,  1.51s/it]

```

In [ ]:
Copied!
```
extract_metadata

```

extract_metadata
Out[ ]:
```
[{'entities': ['eugeneyan', 'llm', 'engineering', 'production'],
  'summary': 'Patterns for Building LLM-based Systems & Products - Discussions on HackerNews, Twitter, and LinkedIn. There is a large class of problems that are easy to imagine and build demos for, but extremely hard to make products out of. For example, self-driving: It’s easy to demo a'}]
```

In [ ]:
Copied!
```
metadata_nodes = metadata_extractor.process_nodes(orig_nodes[0:1])

```

metadata_nodes = metadata_extractor.process_nodes(orig_nodes[0:1])
```
100%|██████████| 1/1 [00:01<00:00,  1.03s/it]

```

In [ ]:
Copied!
```
metadata_nodes

```

metadata_nodes
Out[ ]:
```
[TextNode(id_='2b6a40a8-dd6a-44a8-a005-da32ad98a05c', embedding=None, metadata={'entities': ['eugeneyan', 'llm', 'engineering', 'production'], 'summary': 'Patterns for Building LLM-based Systems & Products - Discussions on HackerNews, Twitter, and LinkedIn. Content includes discussions on self-driving technology and challenges in turning demos into products.'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='https://eugeneyan.com/writing/llm-patterns/', node_type=<ObjectType.DOCUMENT: '4'>, metadata={}, hash='9da2827b0860b2f81e51cb3efd93a13227f0e4312355a495e5668669f257cb14'), <NodeRelationship.NEXT: '3'>: RelatedNodeInfo(node_id='d3a86dba-7579-4196-80d7-30affa7052a7', node_type=<ObjectType.TEXT: '1'>, metadata={}, hash='993e43bb060cf2f183f894f8dec6708eadcac2b7d2760a94916dc82c24255acc')}, text='# [eugeneyan](/)\n\n  * [Start Here](/start-here/ "Start Here")\n  * [Writing](/writing/ "Writing")\n  * [Speaking](/speaking/ "Speaking")\n  * [Prototyping](/prototyping/ "Prototyping")\n  * [About](/about/ "About")\n\n# Patterns for Building LLM-based Systems & Products\n\n[ [llm](/tag/llm/) [engineering](/tag/engineering/)\n[production](/tag/production/) [🔥](/tag/🔥/) ]  · 66 min read\n\n> Discussions on [HackerNews](https://news.ycombinator.com/item?id=36965993),\n> [Twitter](https://twitter.com/eugeneyan/status/1686531758701899776), and\n> [LinkedIn](https://www.linkedin.com/posts/eugeneyan_patterns-for-building-\n> llm-based-systems-activity-7092300473981927424-_wVo)\n\n“There is a large class of problems that are easy to imagine and build demos\nfor, but extremely hard to make products out of. For example, self-driving:\nIt’s easy to demo a', start_char_idx=0, end_char_idx=838, text_template='[Excerpt from document]\n{metadata_str}\nExcerpt:\n-----\n{content}\n-----\n', metadata_template='{key}: {value}', metadata_seperator='\n')]
```

