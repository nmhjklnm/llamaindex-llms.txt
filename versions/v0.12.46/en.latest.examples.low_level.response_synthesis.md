![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Building Response Synthesis from Scratch¶
In this tutorial, we show you how to build the "LLM synthesis" component of a RAG pipeline from scratch. Given a set of retrieved Nodes, we'll show you how to synthesize a response even if the retrieved context overflows the context window.
We'll walk through some synthesis strategies:
  * Create and Refine
  * Tree Summarization


We're essentially unpacking our "Response Synthesis" module and exposing that for the user.
We use OpenAI as a default LLM but you're free to plug in any LLM you wish.
## Setup¶
We build an empty Pinecone Index, and define the necessary LlamaIndex wrappers/abstractions so that we can load/index data and get back a vector retriever.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-file pymupdf
%pip install llama-index-vector-stores-pinecone
%pip install llama-index-llms-openai

```

%pip install llama-index-readers-file pymupdf %pip install llama-index-vector-stores-pinecone %pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
#### Load Data¶
In [ ]:
Copied!
```
!mkdir data
!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"

```

!mkdir data !wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"
In [ ]:
Copied!
```
from pathlib import Path
from llama_index.readers.file import PyMuPDFReader

```

from pathlib import Path from llama_index.readers.file import PyMuPDFReader
In [ ]:
Copied!
```
loader = PyMuPDFReader()
documents = loader.load(file_path="./data/llama2.pdf")

```

loader = PyMuPDFReader() documents = loader.load(file_path="./data/llama2.pdf")
#### Build Pinecone Index, Get Retriever¶
We use our high-level LlamaIndex abstractions to 1) ingest data into Pinecone, and then 2) get a vector retriever.
Note that we set chunk sizes to 1024.
In [ ]:
Copied!
```
import pinecone
import os

api_key = os.environ["PINECONE_API_KEY"]
pinecone.init(api_key=api_key, environment="us-west1-gcp")

```

import pinecone import os api_key = os.environ["PINECONE_API_KEY"] pinecone.init(api_key=api_key, environment="us-west1-gcp")
```
/Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages/pinecone/index.py:4: TqdmExperimentalWarning: Using `tqdm.autonotebook.tqdm` in notebook mode. Use `tqdm.tqdm` instead to force console mode (e.g. in jupyter console)
  from tqdm.autonotebook import tqdm

```

In [ ]:
Copied!
```
# dimensions are for text-embedding-ada-002
pinecone.create_index(
    "quickstart", dimension=1536, metric="euclidean", pod_type="p1"
)

```

# dimensions are for text-embedding-ada-002 pinecone.create_index( "quickstart", dimension=1536, metric="euclidean", pod_type="p1" )
In [ ]:
Copied!
```
pinecone_index = pinecone.Index("quickstart")

```

pinecone_index = pinecone.Index("quickstart")
In [ ]:
Copied!
```
# [Optional] drop contents in index
pinecone_index.delete(deleteAll=True)

```

# [Optional] drop contents in index pinecone_index.delete(deleteAll=True)
Out[ ]:
```
{}
```

In [ ]:
Copied!
```
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import StorageContext

```

from llama_index.vector_stores.pinecone import PineconeVectorStore from llama_index.core import VectorStoreIndex from llama_index.core.node_parser import SentenceSplitter from llama_index.core import StorageContext
In [ ]:
Copied!
```
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
# NOTE: set chunk size of 1024
splitter = SentenceSplitter(chunk_size=1024)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, transformations=[splitter], storage_context=storage_context
)

```

vector_store = PineconeVectorStore(pinecone_index=pinecone_index) # NOTE: set chunk size of 1024 splitter = SentenceSplitter(chunk_size=1024) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex.from_documents( documents, transformations=[splitter], storage_context=storage_context )
In [ ]:
Copied!
```
retriever = index.as_retriever()

```

retriever = index.as_retriever()
#### Given an example question, get a retrieved set of nodes.¶
We use the retriever to get a set of relevant nodes given a user query. These nodes will then be passed to the response synthesis modules below.
In [ ]:
Copied!
```
query_str = (
    "Can you tell me about results from RLHF using both model-based and"
    " human-based evaluation?"
)

```

query_str = ( "Can you tell me about results from RLHF using both model-based and" " human-based evaluation?" )
In [ ]:
Copied!
```
retrieved_nodes = retriever.retrieve(query_str)

```

retrieved_nodes = retriever.retrieve(query_str)
## Building Response Synthesis with LLMs¶
In this section we'll show how to use LLMs + Prompts to build a response synthesis module.
We'll start from simple strategies (simply stuffing context into a prompt), to more advanced strategies that can handle context overflows.
### 1. Try a Simple Prompt¶
We first try to synthesize the response using a single input prompt + LLM call.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

llm = OpenAI(model="text-davinci-003")

```

from llama_index.llms.openai import OpenAI from llama_index.core import PromptTemplate llm = OpenAI(model="text-davinci-003")
In [ ]:
Copied!
```
qa_prompt = PromptTemplate(
    """\
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: \
"""
)

```

qa_prompt = PromptTemplate( """\ Context information is below. --------------------- {context_str} --------------------- Given the context information and not prior knowledge, answer the query. Query: {query_str} Answer: \ """ )
Given an example question, retrieve the set of relevant nodes and try to put it all in the prompt, separated by newlines.
In [ ]:
Copied!
```
query_str = (
    "Can you tell me about results from RLHF using both model-based and"
    " human-based evaluation?"
)

```

query_str = ( "Can you tell me about results from RLHF using both model-based and" " human-based evaluation?" )
In [ ]:
Copied!
```
retrieved_nodes = retriever.retrieve(query_str)

```

retrieved_nodes = retriever.retrieve(query_str)
In [ ]:
Copied!
```
def generate_response(retrieved_nodes, query_str, qa_prompt, llm):
    context_str = "\n\n".join([r.get_content() for r in retrieved_nodes])
    fmt_qa_prompt = qa_prompt.format(
        context_str=context_str, query_str=query_str
    )
    response = llm.complete(fmt_qa_prompt)
    return str(response), fmt_qa_prompt

```

def generate_response(retrieved_nodes, query_str, qa_prompt, llm): context_str = "\n\n".join([r.get_content() for r in retrieved_nodes]) fmt_qa_prompt = qa_prompt.format( context_str=context_str, query_str=query_str ) response = llm.complete(fmt_qa_prompt) return str(response), fmt_qa_prompt
In [ ]:
Copied!
```
response, fmt_qa_prompt = generate_response(
    retrieved_nodes, query_str, qa_prompt, llm
)

```

response, fmt_qa_prompt = generate_response( retrieved_nodes, query_str, qa_prompt, llm )
In [ ]:
Copied!
```
print(f"*****Response******:\n{response}\n\n")

```

print(f"*****Response******:\n{response}\n\n")
```
*****Response******:

RLHF used both model-based and human-based evaluation to select the best-performing models among several ablations. Model-based evaluation was used to measure the robustness of the reward model by collecting a test set of prompts for both helpfulness and safety, and asking three annotators to judge the quality of the answers based on a 7-point Likert scale. Human evaluation was used to validate major model versions. Additionally, a more general reward was trained to ensure the measure wouldn't diverge from the human preferences. Results showed that the reward models were well calibrated with the human preference annotations.


```

In [ ]:
Copied!
```
print(f"*****Formatted Prompt*****:\n{fmt_qa_prompt}\n\n")

```

print(f"*****Formatted Prompt*****:\n{fmt_qa_prompt}\n\n")
```
*****Formatted Prompt*****:
Context information is below.
---------------------
3.4
RLHF Results
3.4.1
Model-Based Evaluation
Evaluating LLMs is a challenging open-research problem. Human evaluation, while a gold standard, can
be complicated by various HCI considerations (Clark et al., 2021; Gehrmann et al., 2023), and is not always
scalable. Thus, to select the best-performing models among several ablations at each iteration from RLHF-V1
to V5, we first observed the improvement of the rewards from the latest reward models, to save costs and
increase iteration speed. We later validated major model versions with human evaluations.
How Far Can Model-Based Evaluation Go?
To measure the robustness of our reward model, we collected
a test set of prompts for both helpfulness and safety, and asked three annotators to judge the quality of the
answers based on a 7-point Likert scale (the higher the better). We observe that our reward models overall
are well calibrated with our human preference annotations, as illustrated in Figure 29 in the appendix. This
confirms the relevance of using our reward as a point-wise metric, despite being trained with a Pairwise
Ranking Loss.
Still, as Goodhart’s Law states, when a measure becomes a target, it ceases to be a good measure. To ensure
our measure won’t diverge from the human preferences, we additionally used a more general reward, trained
17

5
Discussion
Here, we discuss the interesting properties we have observed with RLHF (Section 5.1). We then discuss the
limitations of Llama 2-Chat (Section 5.2). Lastly, we present our strategy for responsibly releasing these
models (Section 5.3).
5.1
Learnings and Observations
Our tuning process revealed several interesting results, such as Llama 2-Chat’s abilities to temporally
organize its knowledge, or to call APIs for external tools.
SFT (Mix)
SFT (Annotation)
RLHF (V1)
0.0
0.2
0.4
0.6
0.8
1.0
Reward Model Score
RLHF (V2)
Figure 20: Distribution shift for progressive versions of Llama 2-Chat, from SFT models towards RLHF.
Beyond Human Supervision.
At the outset of the project, many among us expressed a preference for
supervised annotation, attracted by its denser signal. Meanwhile reinforcement learning, known for its insta-
bility, seemed a somewhat shadowy field for those in the NLP research community. However, reinforcement
learning proved highly effective, particularly given its cost and time effectiveness. Our findings underscore
that the crucial determinant of RLHF’s success lies in the synergy it fosters between humans and LLMs
throughout the annotation process.
Even with proficient annotators, each individual writes with significant variation. A model fine-tuned on
SFT annotation learns this diversity, including, unfortunately, the tail-end of poorly executed annotation. Fur-
thermore, the model’s performance is capped by the writing abilities of the most skilled annotators. Human
annotators are arguably less subject to discrepancy when comparing two outputs’ preference annotation
for RLHF. Consequently, the reward mechanism swiftly learns to assign low scores to undesirable tail-end
distribution and aligns towards the human preference. This phenomena is illustrated in Figure 20, where we
can see that the worst answers are progressively removed, shifting the distribution to the right.
In addition, during annotation, the model has the potential to venture into writing trajectories that even the
best annotators may not chart. Nonetheless, humans can still provide valuable feedback when comparing two
answers, beyond their own writing competencies. Drawing a parallel, while we may not all be accomplished
artists, our ability to appreciate and critique art remains intact. We posit that the superior writing abilities of
LLMs, as manifested in surpassing human annotators in certain tasks, are fundamentally driven by RLHF, as
documented in Gilardi et al. (2023) and Huang et al. (2023). Supervised data may no longer be the gold
standard, and this evolving circumstance compels a re-evaluation of the concept of “supervision.”
In-Context Temperature Rescaling.
We have observed an intriguing phenomenon related to RLHF, a feature
not previously reported to the best of our knowledge: the dynamic re-scaling of temperature contingent upon
the context. As indicated in Figure 8, the temperature appears to be influenced by RLHF. Yet, intriguingly,
our findings also revealed that the shifts are not uniformly applied across all prompts, as shown in Figure 21.
For instance, when it comes to prompts associated with creativity, such as “Write a poem,” an increase in
temperature continues to generate diversity across our various RLHF iterations. This can be observed in the
Self-BLEU slope, which mirrors a pattern comparable to that of the SFT model.
On the other hand, for prompts based on factual information, such as “What is the capital of ?” the Self-BLEU
slope diminishes over time. This pattern suggests that despite the rising temperature, the model learns to
consistently provide the same response to factual prompts.
32
---------------------
Given the context information and not prior knowledge, answer the query.
Query: Can you tell me about results from RLHF using both model-based and human-based evaluation?
Answer: 

```

**Problem** : What if we set the top-k retriever to a higher value? The context would overflow!
In [ ]:
Copied!
```
retriever = index.as_retriever(similarity_top_k=6)
retrieved_nodes = retriever.retrieve(query_str)

```

retriever = index.as_retriever(similarity_top_k=6) retrieved_nodes = retriever.retrieve(query_str)
In [ ]:
Copied!
```
response, fmt_qa_prompt = generate_response(
    retrieved_nodes, query_str, qa_prompt, llm
)
print(f"Response (k=5): {response}")

```

response, fmt_qa_prompt = generate_response( retrieved_nodes, query_str, qa_prompt, llm ) print(f"Response (k=5): {response}")
```
---------------------------------------------------------------------------
ValueError                                Traceback (most recent call last)
Cell In[34], line 1
----> 1 response, fmt_qa_prompt = generate_response(retrieved_nodes, query_str, qa_prompt, llm)
      2 print(f'Response (k=5): {response}')

Cell In[16], line 4, in generate_response(retrieved_nodes, query_str, qa_prompt, llm)
      2 context_str = "\n\n".join([r.get_content() for r in retrieved_nodes])
      3 fmt_qa_prompt = qa_prompt.format(context_str=context_str, query_str=query_str)
----> 4 response = llm.complete(fmt_qa_prompt)
      5 return str(response), fmt_qa_prompt

File ~/Programming/gpt_index/llama_index/llms/base.py:277, in llm_completion_callback.<locals>.wrap.<locals>.wrapped_llm_predict(_self, *args, **kwargs)
    267 with wrapper_logic(_self) as callback_manager:
    268     event_id = callback_manager.on_event_start(
    269         CBEventType.LLM,
    270         payload={
   (...)
    274         },
    275     )
--> 277     f_return_val = f(_self, *args, **kwargs)
    278     if isinstance(f_return_val, Generator):
    279         # intercept the generator and add a callback to the end
    280         def wrapped_gen() -> CompletionResponseGen:

File ~/Programming/gpt_index/llama_index/llms/openai.py:144, in OpenAI.complete(self, prompt, **kwargs)
    142 else:
    143     complete_fn = self._complete
--> 144 return complete_fn(prompt, **kwargs)

File ~/Programming/gpt_index/llama_index/llms/openai.py:281, in OpenAI._complete(self, prompt, **kwargs)
    278 all_kwargs = self._get_all_kwargs(**kwargs)
    279 if self.max_tokens is None:
    280     # NOTE: non-chat completion endpoint requires max_tokens to be set
--> 281     max_tokens = self._get_max_token_for_prompt(prompt)
    282     all_kwargs["max_tokens"] = max_tokens
    284 response = completion_with_retry(
    285     is_chat_model=self._is_chat_model,
    286     max_retries=self.max_retries,
   (...)
    289     **all_kwargs,
    290 )

File ~/Programming/gpt_index/llama_index/llms/openai.py:343, in OpenAI._get_max_token_for_prompt(self, prompt)
    341 max_token = context_window - len(tokens)
    342 if max_token <= 0:
--> 343     raise ValueError(
    344         f"The prompt is too long for the model. "
    345         f"Please use a prompt that is less than {context_window} tokens."
    346     )
    347 return max_token

ValueError: The prompt is too long for the model. Please use a prompt that is less than 4097 tokens.
```

### 2. Try a "Create and Refine" strategy¶
To deal with context overflows, we can try a strategy where we synthesize a response sequentially through all nodes. Start with the first node and generate an initial response. Then for subsequent nodes, refine the answer using additional context.
This requires us to define a "refine" prompt as well.
In [ ]:
Copied!
```
refine_prompt = PromptTemplate(
    """\
The original query is as follows: {query_str}
We have provided an existing answer: {existing_answer}
We have the opportunity to refine the existing answer \
(only if needed) with some more context below.
------------
{context_str}
------------
Given the new context, refine the original answer to better answer the query. \
If the context isn't useful, return the original answer.
Refined Answer: \
"""
)

```

refine_prompt = PromptTemplate( """\ The original query is as follows: {query_str} We have provided an existing answer: {existing_answer} We have the opportunity to refine the existing answer \ (only if needed) with some more context below. ------------ {context_str} ------------ Given the new context, refine the original answer to better answer the query. \ If the context isn't useful, return the original answer. Refined Answer: \ """ )
In [ ]:
Copied!
```
from llama_index.core.response.notebook_utils import display_source_node


def generate_response_cr(
    retrieved_nodes, query_str, qa_prompt, refine_prompt, llm
):
    """Generate a response using create and refine strategy.

    The first node uses the 'QA' prompt.
    All subsequent nodes use the 'refine' prompt.

    """
    cur_response = None
    fmt_prompts = []
    for idx, node in enumerate(retrieved_nodes):
        print(f"[Node {idx}]")
        display_source_node(node, source_length=2000)
        context_str = node.get_content()
        if idx == 0:
            fmt_prompt = qa_prompt.format(
                context_str=context_str, query_str=query_str
            )
        else:
            fmt_prompt = refine_prompt.format(
                context_str=context_str,
                query_str=query_str,
                existing_answer=str(cur_response),
            )

        cur_response = llm.complete(fmt_prompt)
        fmt_prompts.append(fmt_prompt)

    return str(cur_response), fmt_prompts

```

from llama_index.core.response.notebook_utils import display_source_node def generate_response_cr( retrieved_nodes, query_str, qa_prompt, refine_prompt, llm ): """Generate a response using create and refine strategy. The first node uses the 'QA' prompt. All subsequent nodes use the 'refine' prompt. """ cur_response = None fmt_prompts = [] for idx, node in enumerate(retrieved_nodes): print(f"[Node {idx}]") display_source_node(node, source_length=2000) context_str = node.get_content() if idx == 0: fmt_prompt = qa_prompt.format( context_str=context_str, query_str=query_str ) else: fmt_prompt = refine_prompt.format( context_str=context_str, query_str=query_str, existing_answer=str(cur_response), ) cur_response = llm.complete(fmt_prompt) fmt_prompts.append(fmt_prompt) return str(cur_response), fmt_prompts
In [ ]:
Copied!
```
response, fmt_prompts = generate_response_cr(
    retrieved_nodes, query_str, qa_prompt, refine_prompt, llm
)

```

response, fmt_prompts = generate_response_cr( retrieved_nodes, query_str, qa_prompt, refine_prompt, llm )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
In [ ]:
Copied!
```
# view a sample qa prompt
print(fmt_prompts[0])

```

# view a sample qa prompt print(fmt_prompts[0])
In [ ]:
Copied!
```
# view a sample refine prompt
print(fmt_prompts[1])

```

# view a sample refine prompt print(fmt_prompts[1])
**Observation** : This is an initial step, but obviously there are inefficiencies. One is the fact that it's quite slow - we make sequential calls. The second piece is that each LLM call is inefficient - we are only inserting a single node, but not "stuffing" the prompt with as much context as necessary.
### 3. Try a Hierarchical Summarization Strategy¶
Another approach is to try a hierarchical summarization strategy. We generate an answer for each node independently, and then hierarchically combine the answers. This "combine" step could happen once, or for maximum generality can happen recursively until there is one "root" node. That "root" node is then returned as the answer.
We implement this approach below. We have a fixed number of children of 5, so we hierarchically combine 5 children at a time.
**NOTE** : In LlamaIndex this is referred to as "tree_summarize", in LangChain this is referred to as map-reduce.
In [ ]:
Copied!
```
def combine_results(
    texts,
    query_str,
    qa_prompt,
    llm,
    cur_prompt_list,
    num_children=10,
):
    new_texts = []
    for idx in range(0, len(texts), num_children):
        text_batch = texts[idx : idx + num_children]
        context_str = "\n\n".join([t for t in text_batch])
        fmt_qa_prompt = qa_prompt.format(
            context_str=context_str, query_str=query_str
        )
        combined_response = llm.complete(fmt_qa_prompt)
        new_texts.append(str(combined_response))
        cur_prompt_list.append(fmt_qa_prompt)

    if len(new_texts) == 1:
        return new_texts[0]
    else:
        return combine_results(
            new_texts, query_str, qa_prompt, llm, num_children=num_children
        )


def generate_response_hs(
    retrieved_nodes, query_str, qa_prompt, llm, num_children=10
):
    """Generate a response using hierarchical summarization strategy.

    Combine num_children nodes hierarchically until we get one root node.

    """
    fmt_prompts = []
    node_responses = []
    for node in retrieved_nodes:
        context_str = node.get_content()
        fmt_qa_prompt = qa_prompt.format(
            context_str=context_str, query_str=query_str
        )
        node_response = llm.complete(fmt_qa_prompt)
        node_responses.append(node_response)
        fmt_prompts.append(fmt_qa_prompt)

    response_txt = combine_results(
        [str(r) for r in node_responses],
        query_str,
        qa_prompt,
        llm,
        fmt_prompts,
        num_children=num_children,
    )

    return response_txt, fmt_prompts

```

def combine_results( texts, query_str, qa_prompt, llm, cur_prompt_list, num_children=10, ): new_texts = [] for idx in range(0, len(texts), num_children): text_batch = texts[idx : idx + num_children] context_str = "\n\n".join([t for t in text_batch]) fmt_qa_prompt = qa_prompt.format( context_str=context_str, query_str=query_str ) combined_response = llm.complete(fmt_qa_prompt) new_texts.append(str(combined_response)) cur_prompt_list.append(fmt_qa_prompt) if len(new_texts) == 1: return new_texts[0] else: return combine_results( new_texts, query_str, qa_prompt, llm, num_children=num_children ) def generate_response_hs( retrieved_nodes, query_str, qa_prompt, llm, num_children=10 ): """Generate a response using hierarchical summarization strategy. Combine num_children nodes hierarchically until we get one root node. """ fmt_prompts = [] node_responses = [] for node in retrieved_nodes: context_str = node.get_content() fmt_qa_prompt = qa_prompt.format( context_str=context_str, query_str=query_str ) node_response = llm.complete(fmt_qa_prompt) node_responses.append(node_response) fmt_prompts.append(fmt_qa_prompt) response_txt = combine_results( [str(r) for r in node_responses], query_str, qa_prompt, llm, fmt_prompts, num_children=num_children, ) return response_txt, fmt_prompts
In [ ]:
Copied!
```
response, fmt_prompts = generate_response_hs(
    retrieved_nodes, query_str, qa_prompt, llm
)

```

response, fmt_prompts = generate_response_hs( retrieved_nodes, query_str, qa_prompt, llm )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The results from RLHF using both model-based and human-based evaluation showed that Llama 2-Chat models outperformed open-source models by a significant margin on both single turn and multi-turn prompts. For human-based evaluation, we compared Llama 2-Chat models to open-source models and closed-source models on over 4,000 single and multi-turn prompts. The results showed that Llama 2-Chat models outperformed the other models by a significant margin on both single turn and multi-turn prompts. The human preference annotation agreement rate was also higher on more distinct responses than similar pairs. The largest RLHF model was competitive with ChatGPT, with a win rate of 36% and a tie rate of 31.5% relative to ChatGPT. RLHF 70B model also outperformed PaLM-bison chat model by a large percentage on the prompt set.

```

**Observation** : Note that the answer is much more concise than the create-and-refine approach. This is a well-known phemonenon - the reason is because hierarchical summarization tends to compress information at each stage, whereas create and refine encourages adding on more information with each node.
**Observation** : Similar to the above section, there are inefficiencies. We are still generating an answer for each node independently that we can try to optimize away.
Our `ResponseSynthesizer` module handles this!
#### 4. [Optional] Let's create an async version of hierarchical summarization!¶
A pro of the hierarchical summarization approach is that the LLM calls can be parallelized, leading to big speedups in response synthesis.
We implement an async version below. We use asyncio.gather to execute coroutines (LLM calls) for each Node concurrently.
In [ ]:
Copied!
```
import nest_asyncio
import asyncio

nest_asyncio.apply()

```

import nest_asyncio import asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
async def acombine_results(
    texts,
    query_str,
    qa_prompt,
    llm,
    cur_prompt_list,
    num_children=10,
):
    fmt_prompts = []
    for idx in range(0, len(texts), num_children):
        text_batch = texts[idx : idx + num_children]
        context_str = "\n\n".join([t for t in text_batch])
        fmt_qa_prompt = qa_prompt.format(
            context_str=context_str, query_str=query_str
        )
        fmt_prompts.append(fmt_qa_prompt)
        cur_prompt_list.append(fmt_qa_prompt)

    tasks = [llm.acomplete(p) for p in fmt_prompts]
    combined_responses = await asyncio.gather(*tasks)
    new_texts = [str(r) for r in combined_responses]

    if len(new_texts) == 1:
        return new_texts[0]
    else:
        return await acombine_results(
            new_texts, query_str, qa_prompt, llm, num_children=num_children
        )


async def agenerate_response_hs(
    retrieved_nodes, query_str, qa_prompt, llm, num_children=10
):
    """Generate a response using hierarchical summarization strategy.

    Combine num_children nodes hierarchically until we get one root node.

    """
    fmt_prompts = []
    node_responses = []
    for node in retrieved_nodes:
        context_str = node.get_content()
        fmt_qa_prompt = qa_prompt.format(
            context_str=context_str, query_str=query_str
        )
        fmt_prompts.append(fmt_qa_prompt)

    tasks = [llm.acomplete(p) for p in fmt_prompts]
    node_responses = await asyncio.gather(*tasks)

    response_txt = combine_results(
        [str(r) for r in node_responses],
        query_str,
        qa_prompt,
        llm,
        fmt_prompts,
        num_children=num_children,
    )

    return response_txt, fmt_prompts

```

async def acombine_results( texts, query_str, qa_prompt, llm, cur_prompt_list, num_children=10, ): fmt_prompts = [] for idx in range(0, len(texts), num_children): text_batch = texts[idx : idx + num_children] context_str = "\n\n".join([t for t in text_batch]) fmt_qa_prompt = qa_prompt.format( context_str=context_str, query_str=query_str ) fmt_prompts.append(fmt_qa_prompt) cur_prompt_list.append(fmt_qa_prompt) tasks = [llm.acomplete(p) for p in fmt_prompts] combined_responses = await asyncio.gather(*tasks) new_texts = [str(r) for r in combined_responses] if len(new_texts) == 1: return new_texts[0] else: return await acombine_results( new_texts, query_str, qa_prompt, llm, num_children=num_children ) async def agenerate_response_hs( retrieved_nodes, query_str, qa_prompt, llm, num_children=10 ): """Generate a response using hierarchical summarization strategy. Combine num_children nodes hierarchically until we get one root node. """ fmt_prompts = [] node_responses = [] for node in retrieved_nodes: context_str = node.get_content() fmt_qa_prompt = qa_prompt.format( context_str=context_str, query_str=query_str ) fmt_prompts.append(fmt_qa_prompt) tasks = [llm.acomplete(p) for p in fmt_prompts] node_responses = await asyncio.gather(*tasks) response_txt = combine_results( [str(r) for r in node_responses], query_str, qa_prompt, llm, fmt_prompts, num_children=num_children, ) return response_txt, fmt_prompts
In [ ]:
Copied!
```
response, fmt_prompts = await agenerate_response_hs(
    retrieved_nodes, query_str, qa_prompt, llm
)

```

response, fmt_prompts = await agenerate_response_hs( retrieved_nodes, query_str, qa_prompt, llm )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
 Results from RLHF using both model-based and human-based evaluation show that larger models generally obtain higher performance for a similar volume of data. Additionally, the accuracy on more distinct responses matters the most to improve Llama 2-Chat performance. The human preference annotation agreement rate is also higher on more distinct responses than similar pairs. Furthermore, two main algorithms were explored for RLHF fine-tuning: Proximal Policy Optimization (PPO) and Rejection Sampling fine-tuning. The largest Llama 2-Chat model was found to be competitive with ChatGPT, with a win rate of 36% and a tie rate of 31.5% relative to ChatGPT. Additionally, Llama 2-Chat 70B model outperformed PaLM-bison chat model by a large percentage on our prompt set. Inter-Rater Reliability (IRR) was measured using Gwet’s AC1/2 statistic, with scores varying between 0.37 and 0.55 depending on the specific model comparison.

```

## Let's put it all together!¶
Let's define a simple query engine that can be initialized with a retriever, prompt, llm etc. And have it implement a simple `query` function. We also implement an async version, can be used if you completed part 4 above!
**NOTE** : We skip subclassing our own `QueryEngine` abstractions. This is a big TODO to make it more easily sub-classable!
In [ ]:
Copied!
```
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.llms import LLM
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Response:
    response: str
    source_nodes: Optional[List] = None

    def __str__(self):
        return self.response


class MyQueryEngine:
    """My query engine.

    Uses the tree summarize response synthesis module by default.

    """

    def __init__(
        self,
        retriever: BaseRetriever,
        qa_prompt: PromptTemplate,
        llm: LLM,
        num_children=10,
    ) -> None:
        self._retriever = retriever
        self._qa_prompt = qa_prompt
        self._llm = llm
        self._num_children = num_children

    def query(self, query_str: str):
        retrieved_nodes = self._retriever.retrieve(query_str)
        response_txt, _ = generate_response_hs(
            retrieved_nodes,
            query_str,
            self._qa_prompt,
            self._llm,
            num_children=self._num_children,
        )
        response = Response(response_txt, source_nodes=retrieved_nodes)
        return response

    async def aquery(self, query_str: str):
        retrieved_nodes = await self._retriever.aretrieve(query_str)
        response_txt, _ = await agenerate_response_hs(
            retrieved_nodes,
            query_str,
            self._qa_prompt,
            self._llm,
            num_children=self._num_children,
        )
        response = Response(response_txt, source_nodes=retrieved_nodes)
        return response

```

from llama_index.core.retrievers import BaseRetriever from llama_index.core.llms import LLM from dataclasses import dataclass from typing import Optional, List @dataclass class Response: response: str source_nodes: Optional[List] = None def __str__(self): return self.response class MyQueryEngine: """My query engine. Uses the tree summarize response synthesis module by default. """ def __init__( self, retriever: BaseRetriever, qa_prompt: PromptTemplate, llm: LLM, num_children=10, ) -> None: self._retriever = retriever self._qa_prompt = qa_prompt self._llm = llm self._num_children = num_children def query(self, query_str: str): retrieved_nodes = self._retriever.retrieve(query_str) response_txt, _ = generate_response_hs( retrieved_nodes, query_str, self._qa_prompt, self._llm, num_children=self._num_children, ) response = Response(response_txt, source_nodes=retrieved_nodes) return response async def aquery(self, query_str: str): retrieved_nodes = await self._retriever.aretrieve(query_str) response_txt, _ = await agenerate_response_hs( retrieved_nodes, query_str, self._qa_prompt, self._llm, num_children=self._num_children, ) response = Response(response_txt, source_nodes=retrieved_nodes) return response
In [ ]:
Copied!
```
query_engine = MyQueryEngine(retriever, qa_prompt, llm, num_children=10)

```

query_engine = MyQueryEngine(retriever, qa_prompt, llm, num_children=10)
In [ ]:
Copied!
```
response = query_engine.query(query_str)

```

response = query_engine.query(query_str)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The results from RLHF using both model-based and human-based evaluation showed that larger models generally obtained higher performance for a similar volume of data. The accuracy on more distinct responses was higher than on similar pairs, indicating that learning to model human preferences becomes challenging when deciding between two similar model responses. Additionally, the largest Llama 2-Chat model was found to be competitive with ChatGPT, with a win rate of 36% and a tie rate of 31.5% relative to ChatGPT. Llama 2-Chat 70B model was also found to outperform PaLM-bison chat model by a large percentage on the prompt set. Inter-Rater Reliability (IRR) was measured using Gwet’s AC1/2 statistic, with scores varying between 0.37 and 0.55 depending on the specific model comparison.

```

In [ ]:
Copied!
```
response = await query_engine.aquery(query_str)

```

response = await query_engine.aquery(query_str)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The results from RLHF using both model-based and human-based evaluation showed that larger models generally obtained higher performance for a similar volume of data. The accuracy on more distinct responses was higher than on similar pairs, indicating that learning to model human preferences becomes challenging when deciding between two similar model responses. Additionally, the largest Llama 2-Chat model was found to be competitive with ChatGPT, with a win rate of 36% and a tie rate of 31.5%. Human evaluations were conducted using a 7-point Likert scale helpfulness task, with Gwet’s AC2 score varying between 0.37 and 0.55 depending on the specific model comparison.

```

