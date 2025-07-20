![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Custom Cohere Reranker¶
This notebook provides a tutorial on building the Cohere Custom Re-ranker using LlamaIndex abstractions. Upon completion, you'll be able to create a Custom re-ranker and utilize it for enhanced data retrieval.
**Important:** This notebook offers a guide for Cohere Custom Re-ranker. The results presented at the end of this tutorial are unique to the chosen dataset and parameters. We suggest experimenting with your dataset and various parameters before deciding to incorporate it into your RAG pipeline.
## Setup¶
Let's install the necessary packages.
In [ ]:
Copied!
```
%pip install llama-index-postprocessor-cohere-rerank
%pip install llama-index-llms-openai
%pip install llama-index-finetuning
%pip install llama-index-embeddings-cohere

```

%pip install llama-index-postprocessor-cohere-rerank %pip install llama-index-llms-openai %pip install llama-index-finetuning %pip install llama-index-embeddings-cohere
In [ ]:
Copied!
```
!pip install llama-index cohere pypdf

```

!pip install llama-index cohere pypdf
### Initialize the api keys.¶
OpenAI - For creating synthetic dataset.
CohereAI - For training custom reranker and evaluating with base reranker.
In [ ]:
Copied!
```
openai_api_key = "YOUR OPENAI API KEY"
cohere_api_key = "YOUR COHEREAI API KEY"

```

openai_api_key = "YOUR OPENAI API KEY" cohere_api_key = "YOUR COHEREAI API KEY"
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["COHERE_API_KEY"] = cohere_api_key

```

import os os.environ["OPENAI_API_KEY"] = openai_api_key os.environ["COHERE_API_KEY"] = cohere_api_key
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser

# LLM
from llama_index.llms.openai import OpenAI

# Embeddings
from llama_index.embeddings.cohere import CohereEmbedding

# Retrievers
from llama_index.core.retrievers import BaseRetriever, VectorIndexRetriever

# Rerankers
from llama_index.core import QueryBundle
from llama_index.core.indices.query.schema import QueryType
from llama_index.core.schema import NodeWithScore
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.evaluation import EmbeddingQAFinetuneDataset
from llama_index.finetuning import generate_cohere_reranker_finetuning_dataset

# Evaluator
from llama_index.core.evaluation import generate_question_context_pairs
from llama_index.core.evaluation import RetrieverEvaluator

# Finetuner
from llama_index.finetuning import CohereRerankerFinetuneEngine


from typing import List
import pandas as pd

import nest_asyncio

nest_asyncio.apply()

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.node_parser import SimpleNodeParser # LLM from llama_index.llms.openai import OpenAI # Embeddings from llama_index.embeddings.cohere import CohereEmbedding # Retrievers from llama_index.core.retrievers import BaseRetriever, VectorIndexRetriever # Rerankers from llama_index.core import QueryBundle from llama_index.core.indices.query.schema import QueryType from llama_index.core.schema import NodeWithScore from llama_index.postprocessor.cohere_rerank import CohereRerank from llama_index.core.evaluation import EmbeddingQAFinetuneDataset from llama_index.finetuning import generate_cohere_reranker_finetuning_dataset # Evaluator from llama_index.core.evaluation import generate_question_context_pairs from llama_index.core.evaluation import RetrieverEvaluator # Finetuner from llama_index.finetuning import CohereRerankerFinetuneEngine from typing import List import pandas as pd import nest_asyncio nest_asyncio.apply()
## Download data¶
We will use Lyft 2021 10K SEC Filings for training and Uber 2021 10K SEC Filings for evaluating.
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
## Load Data¶
In [ ]:
Copied!
```
lyft_docs = SimpleDirectoryReader(
    input_files=["./data/10k/lyft_2021.pdf"]
).load_data()
uber_docs = SimpleDirectoryReader(
    input_files=["./data/10k/uber_2021.pdf"]
).load_data()

```

lyft_docs = SimpleDirectoryReader( input_files=["./data/10k/lyft_2021.pdf"] ).load_data() uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data()
## Data Curation¶
### Create Nodes.¶
The documentation mentions that Query + Relevant Passage/ Query + Hard Negatives should be less than 510 tokens. To accomidate that we limit chunk_size to 400 tokens. (Each chunk will eventually be treated as a Relevant Passage/ Hard Negative)
In [ ]:
Copied!
```
# Limit chunk size to 400
node_parser = SimpleNodeParser.from_defaults(chunk_size=400)

# Create nodes
lyft_nodes = node_parser.get_nodes_from_documents(lyft_docs)
uber_nodes = node_parser.get_nodes_from_documents(uber_docs)

```

# Limit chunk size to 400 node_parser = SimpleNodeParser.from_defaults(chunk_size=400) # Create nodes lyft_nodes = node_parser.get_nodes_from_documents(lyft_docs) uber_nodes = node_parser.get_nodes_from_documents(uber_docs)
We will use gpt-4 to create questions from chunks.
In [ ]:
Copied!
```
llm = OpenAI(temperature=0, model="gpt-4")

```

llm = OpenAI(temperature=0, model="gpt-4")
Prompt to generate questions from each Node/ chunk.
In [ ]:
Copied!
```
# Prompt to generate questions
qa_generate_prompt_tmpl = """\
Context information is below.

---------------------
{context_str}
---------------------

Given the context information and not prior knowledge.
generate only questions based on the below query.

You are a Professor. Your task is to setup \
{num_questions_per_chunk} questions for an upcoming \
quiz/examination. The questions should be diverse in nature \
across the document. The questions should not contain options, not start with Q1/ Q2. \
Restrict the questions to the context information provided.\
"""

```

# Prompt to generate questions qa_generate_prompt_tmpl = """\ Context information is below. --------------------- {context_str} --------------------- Given the context information and not prior knowledge. generate only questions based on the below query. You are a Professor. Your task is to setup \ {num_questions_per_chunk} questions for an upcoming \ quiz/examination. The questions should be diverse in nature \ across the document. The questions should not contain options, not start with Q1/ Q2. \ Restrict the questions to the context information provided.\ """
Training Custom Re-ranker expects minimum 256 (Query + Relevant passage) pairs with or without hard negatives for training and 64 pairs for validation. Please note that the validation is optional.
**Training:** We use first 256 nodes from Lyft for creating training pairs.
**Validation:** We will use next 64 nodes from Lyft for validation.
**Testing:** We will use 150 nodes from Uber.
In [ ]:
Copied!
```
qa_dataset_lyft_train = generate_question_context_pairs(
    lyft_nodes[:256],
    llm=llm,
    num_questions_per_chunk=1,
    qa_generate_prompt_tmpl=qa_generate_prompt_tmpl,
)

# Save [Optional]
qa_dataset_lyft_train.save_json("lyft_train_dataset.json")

```

qa_dataset_lyft_train = generate_question_context_pairs( lyft_nodes[:256], llm=llm, num_questions_per_chunk=1, qa_generate_prompt_tmpl=qa_generate_prompt_tmpl, ) # Save [Optional] qa_dataset_lyft_train.save_json("lyft_train_dataset.json")
In [ ]:
Copied!
```
qa_dataset_lyft_val = generate_question_context_pairs(
    lyft_nodes[257:321],
    llm=llm,
    num_questions_per_chunk=1,
    qa_generate_prompt_tmpl=qa_generate_prompt_tmpl,
)

# Save [Optional]
qa_dataset_lyft_val.save_json("lyft_val_dataset.json")

```

qa_dataset_lyft_val = generate_question_context_pairs( lyft_nodes[257:321], llm=llm, num_questions_per_chunk=1, qa_generate_prompt_tmpl=qa_generate_prompt_tmpl, ) # Save [Optional] qa_dataset_lyft_val.save_json("lyft_val_dataset.json")
In [ ]:
Copied!
```
qa_dataset_uber_val = generate_question_context_pairs(
    uber_nodes[:150],
    llm=llm,
    num_questions_per_chunk=1,
    qa_generate_prompt_tmpl=qa_generate_prompt_tmpl,
)

# Save [Optional]
qa_dataset_uber_val.save_json("uber_val_dataset.json")

```

qa_dataset_uber_val = generate_question_context_pairs( uber_nodes[:150], llm=llm, num_questions_per_chunk=1, qa_generate_prompt_tmpl=qa_generate_prompt_tmpl, ) # Save [Optional] qa_dataset_uber_val.save_json("uber_val_dataset.json")
Now that we have compiled questions from each chunk, we will format the data according to the specifications required for training the Custom Re-ranker.
### Data Format and Requirements¶
For both training and evaluation, it currently accepts data in the format of triplets, every row should have the following
**query:** this represents the question or target
**relevant_passages:** this represents a list of documents or passages that contain information that answers the query. For every query there must be at least one relevant_passage
**hard_negatives:** this represents chunks or passages that don't contain answer for the query. It should be notes that Hard negatives are optional but providing atleast ~5 hard negatives will lead to meaningful improvement.
Reference
In [ ]:
Copied!
```
# Initialize the Cohere embedding model which we use it for creating Hard Negatives.
embed_model = CohereEmbedding(
    api_key=cohere_api_key,
    model_name="embed-english-v3.0",
    input_type="search_document",
)

```

# Initialize the Cohere embedding model which we use it for creating Hard Negatives. embed_model = CohereEmbedding( api_key=cohere_api_key, model_name="embed-english-v3.0", input_type="search_document", )
Let's create 3 datasets.
  1. Dataset without hard negatives.
  2. Dataset with hard negatives selected at random.
  3. Dataset with hard negatives selected based on cosine similarity.


In [ ]:
Copied!
```
# Train and val datasets without hard negatives.
generate_cohere_reranker_finetuning_dataset(
    qa_dataset_lyft_train, finetune_dataset_file_name="train.jsonl"
)

generate_cohere_reranker_finetuning_dataset(
    qa_dataset_lyft_val, finetune_dataset_file_name="val.jsonl"
)

# Train and val datasets with hard negatives selected at random.
generate_cohere_reranker_finetuning_dataset(
    qa_dataset_lyft_train,
    num_negatives=5,
    hard_negatives_gen_method="random",
    finetune_dataset_file_name="train_5_random.jsonl",
    embed_model=embed_model,
)

generate_cohere_reranker_finetuning_dataset(
    qa_dataset_lyft_val,
    num_negatives=5,
    hard_negatives_gen_method="random",
    finetune_dataset_file_name="val_5_random.jsonl",
    embed_model=embed_model,
)

# Train and val datasets with hard negatives selected based on cosine similarity.
generate_cohere_reranker_finetuning_dataset(
    qa_dataset_lyft_train,
    num_negatives=5,
    hard_negatives_gen_method="cosine_similarity",
    finetune_dataset_file_name="train_5_cosine_similarity.jsonl",
    embed_model=embed_model,
)

generate_cohere_reranker_finetuning_dataset(
    qa_dataset_lyft_val,
    num_negatives=5,
    hard_negatives_gen_method="cosine_similarity",
    finetune_dataset_file_name="val_5_cosine_similarity.jsonl",
    embed_model=embed_model,
)

```

# Train and val datasets without hard negatives. generate_cohere_reranker_finetuning_dataset( qa_dataset_lyft_train, finetune_dataset_file_name="train.jsonl" ) generate_cohere_reranker_finetuning_dataset( qa_dataset_lyft_val, finetune_dataset_file_name="val.jsonl" ) # Train and val datasets with hard negatives selected at random. generate_cohere_reranker_finetuning_dataset( qa_dataset_lyft_train, num_negatives=5, hard_negatives_gen_method="random", finetune_dataset_file_name="train_5_random.jsonl", embed_model=embed_model, ) generate_cohere_reranker_finetuning_dataset( qa_dataset_lyft_val, num_negatives=5, hard_negatives_gen_method="random", finetune_dataset_file_name="val_5_random.jsonl", embed_model=embed_model, ) # Train and val datasets with hard negatives selected based on cosine similarity. generate_cohere_reranker_finetuning_dataset( qa_dataset_lyft_train, num_negatives=5, hard_negatives_gen_method="cosine_similarity", finetune_dataset_file_name="train_5_cosine_similarity.jsonl", embed_model=embed_model, ) generate_cohere_reranker_finetuning_dataset( qa_dataset_lyft_val, num_negatives=5, hard_negatives_gen_method="cosine_similarity", finetune_dataset_file_name="val_5_cosine_similarity.jsonl", embed_model=embed_model, )
## Training Custom Reranker.¶
With our training and validation datasets ready, we're set to proceed with the training Custom re-ranker process. Be aware that this training is expected to take approximately 25 to 45 minutes.
In [ ]:
Copied!
```
# Reranker model with 0 hard negatives.
finetune_model_no_hard_negatives = CohereRerankerFinetuneEngine(
    train_file_name="train.jsonl",
    val_file_name="val.jsonl",
    model_name="lyft_reranker_0_hard_negatives",
    model_type="RERANK",
    base_model="english",
)
finetune_model_no_hard_negatives.finetune()

# Reranker model with 5 hard negatives selected at random
finetune_model_random_hard_negatives = CohereRerankerFinetuneEngine(
    train_file_name="train_5_random.jsonl",
    val_file_name="val_5_random.jsonl",
    model_name="lyft_reranker_5_random_hard_negatives",
    model_type="RERANK",
    base_model="english",
)
finetune_model_random_hard_negatives.finetune()

# Reranker model with 5 hard negatives selected based on cosine similarity
finetune_model_cosine_hard_negatives = CohereRerankerFinetuneEngine(
    train_file_name="train_5_cosine_similarity.jsonl",
    val_file_name="val_5_cosine_similarity.jsonl",
    model_name="lyft_reranker_5_cosine_hard_negatives",
    model_type="RERANK",
    base_model="english",
)
finetune_model_cosine_hard_negatives.finetune()

```

# Reranker model with 0 hard negatives. finetune_model_no_hard_negatives = CohereRerankerFinetuneEngine( train_file_name="train.jsonl", val_file_name="val.jsonl", model_name="lyft_reranker_0_hard_negatives", model_type="RERANK", base_model="english", ) finetune_model_no_hard_negatives.finetune() # Reranker model with 5 hard negatives selected at random finetune_model_random_hard_negatives = CohereRerankerFinetuneEngine( train_file_name="train_5_random.jsonl", val_file_name="val_5_random.jsonl", model_name="lyft_reranker_5_random_hard_negatives", model_type="RERANK", base_model="english", ) finetune_model_random_hard_negatives.finetune() # Reranker model with 5 hard negatives selected based on cosine similarity finetune_model_cosine_hard_negatives = CohereRerankerFinetuneEngine( train_file_name="train_5_cosine_similarity.jsonl", val_file_name="val_5_cosine_similarity.jsonl", model_name="lyft_reranker_5_cosine_hard_negatives", model_type="RERANK", base_model="english", ) finetune_model_cosine_hard_negatives.finetune()
Once the jobs are submitted, you can check the training status in the `models` section of dashboard at https://dashboard.cohere.com/models.
You then need to get the model id for testing.
In [ ]:
Copied!
```
reranker_base = CohereRerank(top_n=5)
reranker_model_0 = finetune_model_no_hard_negatives.get_finetuned_model(
    top_n=5
)
reranker_model_5_random = (
    finetune_model_random_hard_negatives.get_finetuned_model(top_n=5)
)
reranker_model_5_cosine = (
    finetune_model_cosine_hard_negatives.get_finetuned_model(top_n=5)
)

```

reranker_base = CohereRerank(top_n=5) reranker_model_0 = finetune_model_no_hard_negatives.get_finetuned_model( top_n=5 ) reranker_model_5_random = ( finetune_model_random_hard_negatives.get_finetuned_model(top_n=5) ) reranker_model_5_cosine = ( finetune_model_cosine_hard_negatives.get_finetuned_model(top_n=5) )
## Testing¶
We will test out with first 150 nodes from Uber.
  1. Without Reranker.
  2. With Cohere Reranker. (without any training)
  3. With Custom reranker without hard negatives.
  4. With Custom reranker with hard negatives selected at random.
  5. With Custom reranker with hard negatives selected based on cosine similarity.


In [ ]:
Copied!
```
RERANKERS = {
    "WithoutReranker": "None",
    "CohereRerank": reranker_base,
    "CohereRerank_0": reranker_model_0,
    "CohereRerank_5_random": reranker_model_5_random,
    "CohereRerank_5_cosine": reranker_model_5_cosine,
}

```

RERANKERS = { "WithoutReranker": "None", "CohereRerank": reranker_base, "CohereRerank_0": reranker_model_0, "CohereRerank_5_random": reranker_model_5_random, "CohereRerank_5_cosine": reranker_model_5_cosine, }
Function to display the results
In [ ]:
Copied!
```
def display_results(embedding_name, reranker_name, eval_results):
    """Display results from evaluate."""

    metric_dicts = []
    for eval_result in eval_results:
        metric_dict = eval_result.metric_vals_dict
        metric_dicts.append(metric_dict)

    full_df = pd.DataFrame(metric_dicts)

    hit_rate = full_df["hit_rate"].mean()
    mrr = full_df["mrr"].mean()

    metric_df = pd.DataFrame(
        {
            "Embedding": [embedding_name],
            "Reranker": [reranker_name],
            "hit_rate": [hit_rate],
            "mrr": [mrr],
        }
    )

    return metric_df

```

def display_results(embedding_name, reranker_name, eval_results): """Display results from evaluate.""" metric_dicts = [] for eval_result in eval_results: metric_dict = eval_result.metric_vals_dict metric_dicts.append(metric_dict) full_df = pd.DataFrame(metric_dicts) hit_rate = full_df["hit_rate"].mean() mrr = full_df["mrr"].mean() metric_df = pd.DataFrame( { "Embedding": [embedding_name], "Reranker": [reranker_name], "hit_rate": [hit_rate], "mrr": [mrr], } ) return metric_df
In [ ]:
Copied!
```
# Initialize the Cohere embedding model, `input_type` is different for indexing and retrieval.
index_embed_model = CohereEmbedding(
    api_key=cohere_api_key,
    model_name="embed-english-v3.0",
    input_type="search_document",
)

query_embed_model = CohereEmbedding(
    api_key=cohere_api_key,
    model_name="embed-english-v3.0",
    input_type="search_query",
)


vector_index = VectorStoreIndex(
    uber_nodes[:150],
    embed_model=index_embed_model,
)
vector_retriever = VectorIndexRetriever(
    index=vector_index,
    similarity_top_k=10,
    embed_model=query_embed_model,
)

```

# Initialize the Cohere embedding model, `input_type` is different for indexing and retrieval. index_embed_model = CohereEmbedding( api_key=cohere_api_key, model_name="embed-english-v3.0", input_type="search_document", ) query_embed_model = CohereEmbedding( api_key=cohere_api_key, model_name="embed-english-v3.0", input_type="search_query", ) vector_index = VectorStoreIndex( uber_nodes[:150], embed_model=index_embed_model, ) vector_retriever = VectorIndexRetriever( index=vector_index, similarity_top_k=10, embed_model=query_embed_model, )
In [ ]:
Copied!
```
results_df = pd.DataFrame()

embed_name = "CohereEmbedding"

# Loop over rerankers
for rerank_name, reranker in RERANKERS.items():
    print(f"Running Evaluation for Reranker: {rerank_name}")

    # Define Retriever
    class CustomRetriever(BaseRetriever):
        """Custom retriever that performs both Vector search and Knowledge Graph search"""

        def __init__(
            self,
            vector_retriever: VectorIndexRetriever,
        ) -> None:
            """Init params."""

            self._vector_retriever = vector_retriever
            super().__init__()

        def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
            """Retrieve nodes given query."""

            retrieved_nodes = self._vector_retriever.retrieve(query_bundle)

            if reranker != "None":
                retrieved_nodes = reranker.postprocess_nodes(
                    retrieved_nodes, query_bundle
                )
            else:
                retrieved_nodes = retrieved_nodes[:5]

            return retrieved_nodes

        async def _aretrieve(
            self, query_bundle: QueryBundle
        ) -> List[NodeWithScore]:
            """Asynchronously retrieve nodes given query.

            Implemented by the user.

            """
            return self._retrieve(query_bundle)

        async def aretrieve(
            self, str_or_query_bundle: QueryType
        ) -> List[NodeWithScore]:
            if isinstance(str_or_query_bundle, str):
                str_or_query_bundle = QueryBundle(str_or_query_bundle)
            return await self._aretrieve(str_or_query_bundle)

    custom_retriever = CustomRetriever(vector_retriever)

    retriever_evaluator = RetrieverEvaluator.from_metric_names(
        ["mrr", "hit_rate"], retriever=custom_retriever
    )
    eval_results = await retriever_evaluator.aevaluate_dataset(
        qa_dataset_uber_val
    )

    current_df = display_results(embed_name, rerank_name, eval_results)
    results_df = pd.concat([results_df, current_df], ignore_index=True)

```

results_df = pd.DataFrame() embed_name = "CohereEmbedding" # Loop over rerankers for rerank_name, reranker in RERANKERS.items(): print(f"Running Evaluation for Reranker: {rerank_name}") # Define Retriever class CustomRetriever(BaseRetriever): """Custom retriever that performs both Vector search and Knowledge Graph search""" def __init__( self, vector_retriever: VectorIndexRetriever, ) -> None: """Init params.""" self._vector_retriever = vector_retriever super().__init__() def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]: """Retrieve nodes given query.""" retrieved_nodes = self._vector_retriever.retrieve(query_bundle) if reranker != "None": retrieved_nodes = reranker.postprocess_nodes( retrieved_nodes, query_bundle ) else: retrieved_nodes = retrieved_nodes[:5] return retrieved_nodes async def _aretrieve( self, query_bundle: QueryBundle ) -> List[NodeWithScore]: """Asynchronously retrieve nodes given query. Implemented by the user. """ return self._retrieve(query_bundle) async def aretrieve( self, str_or_query_bundle: QueryType ) -> List[NodeWithScore]: if isinstance(str_or_query_bundle, str): str_or_query_bundle = QueryBundle(str_or_query_bundle) return await self._aretrieve(str_or_query_bundle) custom_retriever = CustomRetriever(vector_retriever) retriever_evaluator = RetrieverEvaluator.from_metric_names( ["mrr", "hit_rate"], retriever=custom_retriever ) eval_results = await retriever_evaluator.aevaluate_dataset( qa_dataset_uber_val ) current_df = display_results(embed_name, rerank_name, eval_results) results_df = pd.concat([results_df, current_df], ignore_index=True)
## Check Results.¶
In [ ]:
Copied!
```
print(results_df)

```

print(results_df)
The Cohere Custom Re-ranker has led to improvements. It's important to highlight that determining the optimal number of hard negatives and whether to use random or cosine sampling should be based on experimental results. This guide presents a framework to enhance retrieval systems with Custom Cohere re-ranker.
**There is potential for enhancement in the selection of hard negatives; contributions in this area are welcome from the community.**
