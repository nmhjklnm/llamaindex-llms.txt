# Stress-Testing Long Context LLMs with a Recall Task¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In this section we stress-test long context recall capabilities of GPT-4 and Claude v2. This is inspired by Greg Kamradt's tweet.
Similarly, we analyze the "needle in a haystack" recall capabilities of long-context LLms. We show an incremental extension by 1) adding Claude, and 2) testing recall where context **exceeds** context window, triggering response synthesis strategies.
We use a fixed document - the 2021 Uber 10-K, which contains ~290k tokens.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-llms-anthropic

```

%pip install llama-index-llms-openai %pip install llama-index-llms-anthropic
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, Document
from llama_index.core import SummaryIndex
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.core.evaluation import CorrectnessEvaluator

```

from llama_index.core import SimpleDirectoryReader, Document from llama_index.core import SummaryIndex from llama_index.llms.openai import OpenAI from llama_index.llms.anthropic import Anthropic from llama_index.core.evaluation import CorrectnessEvaluator
## Setup Data / Indexes¶
We load the Uber 10-k
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
```
--2023-11-09 00:35:55--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8000::154, 2606:50c0:8002::154, 2606:50c0:8003::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8000::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1880483 (1.8M) [application/octet-stream]
Saving to: ‘data/10k/uber_2021.pdf’

data/10k/uber_2021. 100%[===================>]   1.79M  --.-KB/s    in 0.1s    

2023-11-09 00:36:04 (18.2 MB/s) - ‘data/10k/uber_2021.pdf’ saved [1880483/1880483]

--2023-11-09 00:36:04--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8000::154, 2606:50c0:8002::154, 2606:50c0:8003::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8000::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1440303 (1.4M) [application/octet-stream]
Saving to: ‘data/10k/lyft_2021.pdf’

data/10k/lyft_2021. 100%[===================>]   1.37M  --.-KB/s    in 0.06s   

2023-11-09 00:36:05 (24.7 MB/s) - ‘data/10k/lyft_2021.pdf’ saved [1440303/1440303]


```

In [ ]:
Copied!
```
## load data
uber_docs0 = SimpleDirectoryReader(
    input_files=["./data/10k/uber_2021.pdf"]
).load_data()
uber_doc = Document(text="\n\n".join([d.get_content() for d in uber_docs0]))

```

## load data uber_docs0 = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data() uber_doc = Document(text="\n\n".join([d.get_content() for d in uber_docs0]))
We print the number of tokens below. Note that this overflows the context window of existing LLMs, requiring response synthesis strategies.
In [ ]:
Copied!
```
# count the number of tokens
from llama_index.core.utils import globals_helper

num_tokens = len(globals_helper.tokenizer(uber_doc.get_content()))
print(f"NUM TOKENS: {num_tokens}")

```

# count the number of tokens from llama_index.core.utils import globals_helper num_tokens = len(globals_helper.tokenizer(uber_doc.get_content())) print(f"NUM TOKENS: {num_tokens}")
```
NUM TOKENS: 291129

```

## Try Out Different Experiments¶
### Define Context String¶
Here we insert a single sentence of context that we're going to "hide" within the overall document at different positions.
In [ ]:
Copied!
```
context_str = "Jerry's favorite snack is Hot Cheetos."
query_str = "What is Jerry's favorite snack?"

```

context_str = "Jerry's favorite snack is Hot Cheetos." query_str = "What is Jerry's favorite snack?"
In [ ]:
Copied!
```
def augment_doc(doc_str, context, position):
    """Augment doc with additional context at a given position."""
    doc_str1 = doc_str[:position]
    doc_str2 = doc_str[position:]

    return f"{doc_str1}...\n\n{context}\n\n...{doc_str2}"

```

def augment_doc(doc_str, context, position): """Augment doc with additional context at a given position.""" doc_str1 = doc_str[:position] doc_str2 = doc_str[position:] return f"{doc_str1}...\n\n{context}\n\n...{doc_str2}"
In [ ]:
Copied!
```
test_str = augment_doc(
    uber_doc.get_content(), context_str, int(0.5 * len(uber_doc.get_content()))
)

```

test_str = augment_doc( uber_doc.get_content(), context_str, int(0.5 * len(uber_doc.get_content())) )
### Define Experiment Loop¶
The experiment loop is the following:
  1. Go through the set of positions (indicated by a percentile relative to the length of the doc)
  2. For each position, inject the context string at that position.
  3. Load the entire doc into our `SummaryIndex`, get the corresponding query engine.
  4. When a question is asked, we trigger response synthesis over the entire document (create-and-refine, or tree summarize).
  5. Compare predicted response against expected response with our `CorrectnessEvaluator`


In [ ]:
Copied!
```
async def run_experiments(
    doc, position_percentiles, context_str, query, llm, response_mode="compact"
):
    eval_llm = OpenAI(model="gpt-4-1106-preview")

    correctness_evaluator = CorrectnessEvaluator(llm=eval_llm)
    eval_scores = {}
    for idx, position_percentile in enumerate(position_percentiles):
        print(f"Position percentile: {position_percentile}")
        position_idx = int(position_percentile * len(uber_doc.get_content()))
        new_doc_str = augment_doc(
            uber_doc.get_content(), context_str, position_idx
        )
        new_doc = Document(text=new_doc_str)
        index = SummaryIndex.from_documents(
            [new_doc],
        )
        query_engine = index.as_query_engine(
            response_mode=response_mode, llm=llm
        )
        print(f"Query: {query}")

        # uncomment for async
        # response = await query_engine.aquery(query)
        response = query_engine.query(query)
        print(f"Response: {str(response)}")
        eval_result = correctness_evaluator.evaluate(
            query=query, response=str(response), reference=context_str
        )
        eval_score = eval_result.score
        print(f"Eval score: {eval_score}")
        eval_scores[position_percentile] = eval_score
    return eval_scores

```

async def run_experiments( doc, position_percentiles, context_str, query, llm, response_mode="compact" ): eval_llm = OpenAI(model="gpt-4-1106-preview") correctness_evaluator = CorrectnessEvaluator(llm=eval_llm) eval_scores = {} for idx, position_percentile in enumerate(position_percentiles): print(f"Position percentile: {position_percentile}") position_idx = int(position_percentile * len(uber_doc.get_content())) new_doc_str = augment_doc( uber_doc.get_content(), context_str, position_idx ) new_doc = Document(text=new_doc_str) index = SummaryIndex.from_documents( [new_doc], ) query_engine = index.as_query_engine( response_mode=response_mode, llm=llm ) print(f"Query: {query}") # uncomment for async # response = await query_engine.aquery(query) response = query_engine.query(query) print(f"Response: {str(response)}") eval_result = correctness_evaluator.evaluate( query=query, response=str(response), reference=context_str ) eval_score = eval_result.score print(f"Eval score: {eval_score}") eval_scores[position_percentile] = eval_score return eval_scores
In [ ]:
Copied!
```
position_percentiles = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

```

position_percentiles = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4-1106-preview")

eval_scores_gpt4 = await run_experiments(
    [uber_doc],
    position_percentiles,
    context_str,
    query_str,
    llm,
    response_mode="compact",
)

```

llm = OpenAI(model="gpt-4-1106-preview") eval_scores_gpt4 = await run_experiments( [uber_doc], position_percentiles, context_str, query_str, llm, response_mode="compact", )
```
Position percentile: 0.0
Query: What is Jerry's favorite snack?
Response: Hot Cheetos.
Eval score: 5.0
Position percentile: 0.1
Query: What is Jerry's favorite snack?
Response: Hot Cheetos.
Eval score: 5.0
Position percentile: 0.2
Query: What is Jerry's favorite snack?
Response: Hot Cheetos.
Eval score: 5.0
Position percentile: 0.3
Query: What is Jerry's favorite snack?
Response: Hot Cheetos.
Eval score: 5.0
Position percentile: 0.4
Query: What is Jerry's favorite snack?
Response: Hot Cheetos.
Eval score: 5.0
Position percentile: 0.5
Query: What is Jerry's favorite snack?
Response: Jerry's favorite snack is not specified in the provided information.
Eval score: 2.0
Position percentile: 0.6
Query: What is Jerry's favorite snack?
Response: Repeat the original answer.
Eval score: 1.0
Position percentile: 0.7
Query: What is Jerry's favorite snack?
Response: Repeat the original answer.
Eval score: 1.0
Position percentile: 0.8
Query: What is Jerry's favorite snack?
Response: Jerry's favorite snack is Hot Cheetos.
Eval score: 5.0
Position percentile: 0.9
Query: What is Jerry's favorite snack?
Response: Jerry's favorite snack is Hot Cheetos.
Eval score: 5.0
Position percentile: 1.0
Query: What is Jerry's favorite snack?
Response: Hot Cheetos.
Eval score: 5.0

```

In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4-1106-preview")
eval_scores_gpt4_ts = await run_experiments(
    [uber_doc],
    position_percentiles,
    context_str,
    query_str,
    llm,
    response_mode="tree_summarize",
)

```

llm = OpenAI(model="gpt-4-1106-preview") eval_scores_gpt4_ts = await run_experiments( [uber_doc], position_percentiles, context_str, query_str, llm, response_mode="tree_summarize", )
```
Position percentile: 0.0
Query: What is Jerry's favorite snack?
Response: Jerry's favorite snack is Hot Cheetos.
Eval score: 5.0
Position percentile: 0.1
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack from the information provided.
Eval score: 1.0
Position percentile: 0.2
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack as there is no information provided about Jerry or his snack preferences.
Eval score: 2.0
Position percentile: 0.3
Query: What is Jerry's favorite snack?
Response: Jerry's favorite snack is Hot Cheetos.
Eval score: 5.0
Position percentile: 0.4
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack from the information provided.
Eval score: 1.0
Position percentile: 0.5
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack from the information available.
Eval score: 2.0
Position percentile: 0.6
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack as there is no information provided about his preferences.
Eval score: 2.0
Position percentile: 0.7
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack from the information provided.
Eval score: 1.0
Position percentile: 0.8
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack as there is no information provided about Jerry's preferences.
Eval score: 2.0
Position percentile: 0.9
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack from the information provided.
Eval score: 1.0
Position percentile: 1.0
Query: What is Jerry's favorite snack?
Response: It is not possible to determine Jerry's favorite snack from the information available.
Eval score: 2.0

```

In [ ]:
Copied!
```
llm = Anthropic(model="claude-2")

eval_scores_anthropic = await run_experiments(
    [uber_doc], position_percentiles, context_str, query_str, llm
)

```

llm = Anthropic(model="claude-2") eval_scores_anthropic = await run_experiments( [uber_doc], position_percentiles, context_str, query_str, llm )
```
Position percentile: 0.0
Query: What is Jerry's favorite snack?
Response:  Unfortunately I do not have enough context to determine what Jerry's favorite snack is, as the new context provided does not contain any information about his preferences or favorite snacks. Without more details about Jerry as an individual, I cannot refine my original answer about his favorite snack. I would need additional information about his tastes, habits, or direct statements from him about his snack preferences in order to update my response. The new context alone does not give me any clues to determine his favorite snack.
Eval score: 2.0
Position percentile: 0.1
Query: What is Jerry's favorite snack?
Response:  I apologize, but the new context you provided does not contain any information about someone named Jerry or what his favorite snack is. The new context discusses an intercreditor agreement, secured obligations, liens and other legal/financial details related to Uber Technologies. It does not mention anything about a person named Jerry or his favorite snacks. Since the new context does not provide any relevant information, I do not have enough details to determine or provide an answer regarding Jerry's favorite snack.
Eval score: 1.0
Position percentile: 0.2
Query: What is Jerry's favorite snack?
Response:  Unfortunately I do not have enough context to determine what Jerry's favorite snack is. The new context provided does not contain any specific information about Jerry's snack preferences. Without more details about Jerry as an individual, such as his tastes, habits, or direct statements about favorite snacks, I cannot confidently provide or refine an answer. I apologize that I cannot give a more substantive response without additional relevant information about Jerry's favorite snack.
Eval score: 2.0
Position percentile: 0.3
Query: What is Jerry's favorite snack?
Response:  Unfortunately I do not have enough context to determine Jerry's favorite snack. The original answer stated that this information was not provided in the context, and the new context does not add any relevant details about Jerry's preferences. Since the original answer already indicated the favorite snack was not mentioned, and the new context does not provide any additional relevant information, I cannot refine the original answer further.
Eval score: 2.0
Position percentile: 0.4
Query: What is Jerry's favorite snack?
Response:  Unfortunately I do not have enough context to determine what Jerry's favorite snack is. The passage provided is an excerpt from a loan agreement that does not mention anyone named Jerry or provide information about snack preferences. The passage defines lien intercreditor agreement terms, but does not give any information about a person named Jerry or their favorite snacks. Without more context about Jerry and his preferences, I cannot infer what his favorite snack is based solely on the loan agreement terms provided in the new context.
Eval score: 1.0
Position percentile: 0.5
Query: What is Jerry's favorite snack?
Response:  I do not have enough context to determine what Jerry's favorite snack is, as the excerpt from Uber's annual 10-K filing provided does not mention anyone named Jerry or provide any details about snack preferences. The passage discusses Uber's business operations and financials, but does not contain information to infer what a specific person named Jerry's favorite snack may be. Without more details about who Jerry is and the context for the question, I cannot determine Jerry's favorite snack based solely on this 10-K excerpt.
Eval score: 1.0
Position percentile: 0.6
Query: What is Jerry's favorite snack?
Response:  Unfortunately I do not have enough context to determine what Jerry's favorite snack is based on the new information provided. The new context is an excerpt from Uber's credit agreement and does not mention anything about a person named Jerry or provide any clues about his favorite snack. Since the new information does not give any details relevant to the original question, I cannot refine my previous response about Jerry's favorite snack. My original answer stating that there is insufficient information to determine Jerry's favorite snack remains applicable.
Eval score: 1.0
Position percentile: 0.7
Query: What is Jerry's favorite snack?
Response:  I apologize, but the passage provided does not contain any information about someone named Jerry or their favorite snack. The passage discusses intercreditor agreements, secured obligations and other financial and legal matters unrelated to an individual's snack preferences. Without any context about Jerry or snacks mentioned in the passage, I do not have enough information to determine what Jerry's favorite snack is.
Eval score: 1.0
Position percentile: 0.8
Query: What is Jerry's favorite snack?
Response:  Unfortunately I do not have enough context to determine what Jerry's favorite snack is, as the provided information is about Uber's financial agreements and does not mention anything about a person named Jerry or his snack preferences. The new context given does not provide any additional clues to help identify Jerry's favorite snack. I would need more specific information about Jerry as an individual to be able to determine his favorite snack.
Eval score: 1.0
Position percentile: 0.9
Query: What is Jerry's favorite snack?
Response:  Unfortunately the new context you provided does not contain any information about Jerry or his favorite snack. The passage discusses intercreditor agreements, amendments, assignments, and other financial and legal matters related to Uber, but does not mention anything about a person named Jerry or provide any clues as to what his favorite snack might be. Since the new context does not add any relevant information about Jerry or his favorite snack, I do not have enough context to determine what Jerry's favorite snack is. My original response that there is insufficient context to determine Jerry's favorite snack remains applicable.
Eval score: 1.0
Position percentile: 1.0
Query: What is Jerry's favorite snack?
Response:  Based on the additional context provided, Jerry's favorite snack is Hot Cheetos.
Eval score: 5.0

```

In [ ]:
Copied!
```
# NOTE: incomplete, running into timeout errors
llm = Anthropic(model="claude-2")
eval_scores_anthropic = await run_experiments(
    [uber_doc],
    position_percentiles,
    context_str,
    query_str,
    llm,
    response_mode="tree_summarize",
)

```

# NOTE: incomplete, running into timeout errors llm = Anthropic(model="claude-2") eval_scores_anthropic = await run_experiments( [uber_doc], position_percentiles, context_str, query_str, llm, response_mode="tree_summarize", )
