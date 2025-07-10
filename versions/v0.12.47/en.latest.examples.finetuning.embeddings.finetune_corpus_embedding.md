# Finetuning corpus embeddings using NUDGE¶
NUDGE is a novel simple and lightweight fine-tuning method that boosts accuracy when retrieving text using semantic similarity with pre-trained embedding models. NUDGE directly modifies the embeddings of data records to maximize the similarity between training queries and their ground-truth answers. NUDGE does so non-parametrically. Non-parametric means that NUDGE does not modify model parameters to generate better embeddings, as fine-tuning the embedding model, or training adaptors would. Instead, NUDGE directly changes the embeddings themselves. Compared with fine-tuning the pre-trained model and training adaptors, NUDGE provides 3.3x and 4.3x higher increase in accuracy and runs 200x and 3x faster, respectively. Here is a blog post on NUDGE, and here is the paper with more details.
We demonstrate NUDGE's effectiveness on a commonly used Information Retrieval benchmark called Scifact.
In [ ]:
Copied!
```
%pip install llama-index-experimental llama-index-embeddings-huggingface nudge-ft torch datasets

```

%pip install llama-index-experimental llama-index-embeddings-huggingface nudge-ft torch datasets
## Load the scifact benchmark¶
In [ ]:
Copied!
```
from llama_index.finetuning import EmbeddingQAFinetuneDataset
from datasets import load_dataset


def load_hf_dataset(dataset_name):
    hf_dataset_name = f"sepz/{dataset_name}_ft"
    corpus = load_dataset(hf_dataset_name, "data_records", split="train")

    queries_train = load_dataset(hf_dataset_name, "qs", split="train")
    queries_validation = load_dataset(hf_dataset_name, "qs", split="dev")
    queries_test = load_dataset(hf_dataset_name, "qs", split="test")

    qrels_train = load_dataset(hf_dataset_name, "qs_rel", split="train")
    qrels_validation = load_dataset(hf_dataset_name, "qs_rel", split="dev")
    qrels_test = load_dataset(hf_dataset_name, "qs_rel", split="test")

    corpus = {
        str(corpus[i]["record_id"]): corpus[i]["text"]
        for i in range(len(corpus))
    }

    queries_train = {
        str(queries_train[i]["q_id"]): queries_train[i]["input"]
        for i in range(len(queries_train))
    }
    queries_validation = {
        str(r["q_id"]): r["input"] for r in queries_validation
    }
    queries_test = {str(r["q_id"]): r["input"] for r in queries_test}

    qrels_train = (
        qrels_train.to_pandas()
        .groupby("q_id")["record_id"]
        .apply(list)
        .to_dict()
    )
    qrels_validation = (
        qrels_validation.to_pandas()
        .groupby("q_id")["record_id"]
        .apply(list)
        .to_dict()
    )
    qrels_test = (
        qrels_test.to_pandas()
        .groupby("q_id")["record_id"]
        .apply(list)
        .to_dict()
    )
    # convert to strings
    qrels_train = {str(k): [str(i) for i in v] for k, v in qrels_train.items()}
    qrels_validation = {
        str(k): [str(i) for i in v] for k, v in qrels_validation.items()
    }
    qrels_test = {str(k): [str(i) for i in v] for k, v in qrels_test.items()}

    # Load the dataset
    train_dataset = EmbeddingQAFinetuneDataset(
        corpus=corpus, queries=queries_train, relevant_docs=qrels_train
    )
    validation_dataset = EmbeddingQAFinetuneDataset(
        corpus=corpus,
        queries=queries_validation,
        relevant_docs=qrels_validation,
    )
    test_dataset = EmbeddingQAFinetuneDataset(
        corpus=corpus, queries=queries_test, relevant_docs=qrels_test
    )

    return train_dataset, validation_dataset, test_dataset

```

from llama_index.finetuning import EmbeddingQAFinetuneDataset from datasets import load_dataset def load_hf_dataset(dataset_name): hf_dataset_name = f"sepz/{dataset_name}_ft" corpus = load_dataset(hf_dataset_name, "data_records", split="train") queries_train = load_dataset(hf_dataset_name, "qs", split="train") queries_validation = load_dataset(hf_dataset_name, "qs", split="dev") queries_test = load_dataset(hf_dataset_name, "qs", split="test") qrels_train = load_dataset(hf_dataset_name, "qs_rel", split="train") qrels_validation = load_dataset(hf_dataset_name, "qs_rel", split="dev") qrels_test = load_dataset(hf_dataset_name, "qs_rel", split="test") corpus = { str(corpus[i]["record_id"]): corpus[i]["text"] for i in range(len(corpus)) } queries_train = { str(queries_train[i]["q_id"]): queries_train[i]["input"] for i in range(len(queries_train)) } queries_validation = { str(r["q_id"]): r["input"] for r in queries_validation } queries_test = {str(r["q_id"]): r["input"] for r in queries_test} qrels_train = ( qrels_train.to_pandas() .groupby("q_id")["record_id"] .apply(list) .to_dict() ) qrels_validation = ( qrels_validation.to_pandas() .groupby("q_id")["record_id"] .apply(list) .to_dict() ) qrels_test = ( qrels_test.to_pandas() .groupby("q_id")["record_id"] .apply(list) .to_dict() ) # convert to strings qrels_train = {str(k): [str(i) for i in v] for k, v in qrels_train.items()} qrels_validation = { str(k): [str(i) for i in v] for k, v in qrels_validation.items() } qrels_test = {str(k): [str(i) for i in v] for k, v in qrels_test.items()} # Load the dataset train_dataset = EmbeddingQAFinetuneDataset( corpus=corpus, queries=queries_train, relevant_docs=qrels_train ) validation_dataset = EmbeddingQAFinetuneDataset( corpus=corpus, queries=queries_validation, relevant_docs=qrels_validation, ) test_dataset = EmbeddingQAFinetuneDataset( corpus=corpus, queries=queries_test, relevant_docs=qrels_test ) return train_dataset, validation_dataset, test_dataset
```
INFO:datasets:PyTorch version 2.5.0a0+872d972e41.nv24.8 available.
PyTorch version 2.5.0a0+872d972e41.nv24.8 available.

```

```
/usr/local/lib/python3.10/dist-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

## Load the dataset and base embedding model¶
In [ ]:
Copied!
```
from llama_index.core.embeddings import resolve_embed_model

train_dataset, val_dataset, test_dataset = load_hf_dataset("scifact")
base_embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

```

from llama_index.core.embeddings import resolve_embed_model train_dataset, val_dataset, test_dataset = load_hf_dataset("scifact") base_embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
```
INFO:sentence_transformers.SentenceTransformer:Load pretrained SentenceTransformer: BAAI/bge-small-en-v1.5
Load pretrained SentenceTransformer: BAAI/bge-small-en-v1.5
INFO:sentence_transformers.SentenceTransformer:2 prompts are loaded, with the keys: ['query', 'text']
2 prompts are loaded, with the keys: ['query', 'text']

```

If we take a peek at the dataset, we can see that its structured as
  * courpus: mapping of document ID to text
  * queries: mapping of query ID to query text
  * relevant_docs: a mapping of query ID to list of document IDs


In [ ]:
Copied!
```
print(val_dataset.queries["2"])

```

print(val_dataset.queries["2"])
```
Depletion of nitric oxide is responsible for vasospasm.

```

In [ ]:
Copied!
```
print(val_dataset.relevant_docs["2"])

```

print(val_dataset.relevant_docs["2"])
```
['552']

```

In [ ]:
Copied!
```
print(val_dataset.corpus["552"])

```

print(val_dataset.corpus["552"])
```
CONTEXT Delayed cerebral vasospasm causes permanent neurological deficits or death in at least 15% of patients following otherwise successful treatment for ruptured intracranial aneurysm. Decreased bioavailability of nitric oxide has been associated with the development of cerebral vasospasm. OBJECTIVE To determine whether infusions of nitrite will prevent delayed cerebral vasospasm. DESIGN, SETTING, AND SUBJECTS A total of 14 anesthetized cynomolgus monkeys had an autologous blood clot placed around the right middle cerebral artery. Cerebral arteriography was performed before clot placement and on days 7 and 14 to assess vasospasm. The study was conducted from August 2003 to February 2004. INTERVENTIONS A 90-mg sodium nitrite intravenous solution infused over 24 hours plus a 45-mg sodium nitrite bolus daily (n = 3); a 180-mg sodium nitrite intravenous solution infused over 24 hours (n = 3); or a control saline solution infusion (n = 8). Each was infused continuously for 14 days. MAIN OUTCOME MEASURES Nitrite, S-nitrosothiol, and methemoglobin levels in blood and cerebrospinal fluid and degree of arteriographic vasospasm. RESULTS In control monkeys, mean (SD) cerebrospinal fluid nitrite levels decreased from 3.1 (1.5) micromol/L to 0.4 (0.1) micromol/L at day 7 and to 0.4 (0.4) micromol/L at day 14 (P = .03). All 8 control monkeys developed significant vasospasm of the right middle cerebral artery, which was complicated by stroke and death in 1 animal. Sodium nitrite infusions increased the nitrite and methemoglobin levels (<2.1% of total hemoglobin) in the blood and cerebrospinal fluid without evoking systemic hypotension. Nitrite infusion prevented development of vasospasm (no animals developed significant vasospasm; mean [SD] reduction in right middle cerebral artery area on day 7 after subarachnoid hemorrhage of 8% [9%] in nitrite-treated monkeys vs 47% [5%] in saline-treated controls; P<.001). There was a negative correlation between the concentration of nitrite in cerebrospinal fluid and the degree of cerebral vasospasm (P<.001). Pharmacological effects of nitrite infusion were also associated with the formation of S-nitrosothiol in cerebrospinal fluid. There was no clinical or pathological evidence of nitrite toxicity. CONCLUSION Subacute sodium nitrite infusions prevented delayed cerebral vasospasm in a primate model of subarachnoid hemorrhage.

```

### Using your own Datasets¶
As you can see, you can run this notebook on any dataset, as long as you have queries and a mapping to relevant documents! If you have documents but are missing a training set of queries checkout the our tools for generating a synthetic dataset (1).
If you wanted, you could also write your own dataset, or even use llama-index to create your own.
Uncomment the code below and add your own files if you want to try it out.
In [ ]:
Copied!
```
# This code would generate your own dataset against your own custom data
from llama_index.finetuning import generate_qa_embedding_pairs
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.evaluation import EmbeddingQAFinetuneDataset


def load_corpus(files, verbose=False):
    if verbose:
        print(f"Loading files {files}")

    reader = SimpleDirectoryReader(input_files=files)
    docs = reader.load_data()
    if verbose:
        print(f"Loaded {len(docs)} docs")

    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(docs, show_progress=verbose)

    if verbose:
        print(f"Parsed {len(nodes)} nodes")

    return nodes


# Load data
# train_nodes = load_corpus(["file1.pdf", ...], verbose=True)
# val_nodes = load_corpus(["file2.pdf", ...], verbose=True)

# Generate pairs
# train_dataset = generate_qa_embedding_pairs(train_nodes)
# val_dataset = generate_qa_embedding_pairs(val_nodes)

# [Optional] Save to disk
# train_dataset.save_json("train_dataset.json")
# val_dataset.save_json("val_dataset.json")

# [Optional] Load
# train_dataset = EmbeddingQAFinetuneDataset.from_json("train_dataset.json")
# val_dataset = EmbeddingQAFinetuneDataset.from_json("val_dataset.json")

```

# This code would generate your own dataset against your own custom data from llama_index.finetuning import generate_qa_embedding_pairs from llama_index.core import SimpleDirectoryReader from llama_index.core.node_parser import SentenceSplitter from llama_index.core.evaluation import EmbeddingQAFinetuneDataset def load_corpus(files, verbose=False): if verbose: print(f"Loading files {files}") reader = SimpleDirectoryReader(input_files=files) docs = reader.load_data() if verbose: print(f"Loaded {len(docs)} docs") parser = SentenceSplitter() nodes = parser.get_nodes_from_documents(docs, show_progress=verbose) if verbose: print(f"Parsed {len(nodes)} nodes") return nodes # Load data # train_nodes = load_corpus(["file1.pdf", ...], verbose=True) # val_nodes = load_corpus(["file2.pdf", ...], verbose=True) # Generate pairs # train_dataset = generate_qa_embedding_pairs(train_nodes) # val_dataset = generate_qa_embedding_pairs(val_nodes) # [Optional] Save to disk # train_dataset.save_json("train_dataset.json") # val_dataset.save_json("val_dataset.json") # [Optional] Load # train_dataset = EmbeddingQAFinetuneDataset.from_json("train_dataset.json") # val_dataset = EmbeddingQAFinetuneDataset.from_json("val_dataset.json")
## Evaluation¶
A common Information Retrieval metric to report during evaluation is NDCG@k.
In [ ]:
Copied!
```
from typing import Optional, Dict

import torch
import numpy as np
from tqdm import tqdm
from llama_index.core.schema import TextNode
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core import VectorStoreIndex


def build_retriever(
    corpus: Dict[str, str],
    embed_model: BaseEmbedding | str,
    corpus_embeddings: Optional[torch.Tensor] = None,
    k: int = 10,
) -> BaseRetriever:
    nodes = []
    for i, (id_, text) in enumerate(corpus.items()):
        if corpus_embeddings is not None:
            nodes.append(
                TextNode(
                    id_=id_, text=text, embedding=corpus_embeddings[i].tolist()
                )
            )
        else:
            nodes.append(TextNode(id_=id_, text=text))

    index = VectorStoreIndex(
        nodes=nodes,
        embeddings=corpus_embeddings,
        embed_model=embed_model,
        show_progress=True,
    )
    return index.as_retriever(similarity_top_k=k)


def ndcg_at_k(
    dataset: EmbeddingQAFinetuneDataset, retriever: BaseRetriever, k: int = 10
):
    queries = dataset.queries
    relevant_docs = dataset.relevant_docs
    ndcg_scores = []
    for query_id, query in tqdm(queries.items()):
        retrieved_nodes = retriever.retrieve(query)
        retrieved_ids = [node.node.node_id for node in retrieved_nodes]
        expected_ids = relevant_docs[query_id]

        # Calculate NDCG
        ideal_dcg = np.sum(
            [1 / np.log2(i + 2) for i in range(min(k, len(expected_ids)))]
        )
        rel_scores = np.zeros(k)
        for j in range(min(k, len(retrieved_ids))):
            if retrieved_ids[j] in expected_ids:
                rel_scores[j] = 1
        dcg = np.sum(
            [rel_scores[i] / np.log2(i + 2) for i in range(len(rel_scores))]
        )
        ndcg = dcg / ideal_dcg if ideal_dcg > 0 else 0

        ndcg_scores.append(ndcg)

    mean_ndcg = np.mean(ndcg_scores)
    return mean_ndcg

```

from typing import Optional, Dict import torch import numpy as np from tqdm import tqdm from llama_index.core.schema import TextNode from llama_index.core.base.embeddings.base import BaseEmbedding from llama_index.core.base.base_retriever import BaseRetriever from llama_index.core import VectorStoreIndex def build_retriever( corpus: Dict[str, str], embed_model: BaseEmbedding | str, corpus_embeddings: Optional[torch.Tensor] = None, k: int = 10, ) -> BaseRetriever: nodes = [] for i, (id_, text) in enumerate(corpus.items()): if corpus_embeddings is not None: nodes.append( TextNode( id_=id_, text=text, embedding=corpus_embeddings[i].tolist() ) ) else: nodes.append(TextNode(id_=id_, text=text)) index = VectorStoreIndex( nodes=nodes, embeddings=corpus_embeddings, embed_model=embed_model, show_progress=True, ) return index.as_retriever(similarity_top_k=k) def ndcg_at_k( dataset: EmbeddingQAFinetuneDataset, retriever: BaseRetriever, k: int = 10 ): queries = dataset.queries relevant_docs = dataset.relevant_docs ndcg_scores = [] for query_id, query in tqdm(queries.items()): retrieved_nodes = retriever.retrieve(query) retrieved_ids = [node.node.node_id for node in retrieved_nodes] expected_ids = relevant_docs[query_id] # Calculate NDCG ideal_dcg = np.sum( [1 / np.log2(i + 2) for i in range(min(k, len(expected_ids)))] ) rel_scores = np.zeros(k) for j in range(min(k, len(retrieved_ids))): if retrieved_ids[j] in expected_ids: rel_scores[j] = 1 dcg = np.sum( [rel_scores[i] / np.log2(i + 2) for i in range(len(rel_scores))] ) ndcg = dcg / ideal_dcg if ideal_dcg > 0 else 0 ndcg_scores.append(ndcg) mean_ndcg = np.mean(ndcg_scores) return mean_ndcg
## Get the corpus embedding finetuning results¶
Next we use, NUDGE, the state of the art method for finetuning corpus embeddings to maximize the accuracy of k-NN retrieval. We then take our new corpus embeddings along with the original embedding model to build a retriever. NUDGE only finetunes the corpus embeddings and does not change any of the parameters in the base embedding model.
In [ ]:
Copied!
```
%%capture
from llama_index.experimental import Nudge

k = 10

nudge = Nudge(
    train_dataset=train_dataset,
    val_dataset=val_dataset,
    embed_model=base_embed_model,
    use_nudge_n=True,
)
nudge.finetune()
nudge_corpus_embeddings = nudge.get_finetuned_corpus_embeddings()
nudge_retriever = build_retriever(
    train_dataset.corpus, base_embed_model, nudge_corpus_embeddings, k=k
)
nudge_ndcg_test = ndcg_at_k(test_dataset, nudge_retriever, k)

```

%%capture from llama_index.experimental import Nudge k = 10 nudge = Nudge( train_dataset=train_dataset, val_dataset=val_dataset, embed_model=base_embed_model, use_nudge_n=True, ) nudge.finetune() nudge_corpus_embeddings = nudge.get_finetuned_corpus_embeddings() nudge_retriever = build_retriever( train_dataset.corpus, base_embed_model, nudge_corpus_embeddings, k=k ) nudge_ndcg_test = ndcg_at_k(test_dataset, nudge_retriever, k)
```
INFO:llama_index.experimental.nudge.base:Use pytorch device: cuda
Use pytorch device: cuda

```

## Get the adapter finetuning results¶
In [ ]:
Copied!
```
%%capture
from llama_index.finetuning import EmbeddingAdapterFinetuneEngine

embedding_adapater_finetune_engine = EmbeddingAdapterFinetuneEngine(
    train_dataset,
    base_embed_model,
    epochs=4,
    batch_size=10,
)
embedding_adapater_finetune_engine.finetune()
embedding_adapter_model = (
    embedding_adapater_finetune_engine.get_finetuned_model()
)
ft_retriever = build_retriever(
    train_dataset.corpus, embedding_adapter_model, k=k
)
ft_ndcg_test = ndcg_at_k(test_dataset, ft_retriever, k)

```

%%capture from llama_index.finetuning import EmbeddingAdapterFinetuneEngine embedding_adapater_finetune_engine = EmbeddingAdapterFinetuneEngine( train_dataset, base_embed_model, epochs=4, batch_size=10, ) embedding_adapater_finetune_engine.finetune() embedding_adapter_model = ( embedding_adapater_finetune_engine.get_finetuned_model() ) ft_retriever = build_retriever( train_dataset.corpus, embedding_adapter_model, k=k ) ft_ndcg_test = ndcg_at_k(test_dataset, ft_retriever, k)
```
INFO:llama_index.finetuning.embeddings.adapter:Use pytorch device: cuda
Use pytorch device: cuda
INFO:llama_index.embeddings.adapter.base:Use pytorch device: cuda
Use pytorch device: cuda

```

## Get the baseline results¶
In [ ]:
Copied!
```
%%capture

base_retriever = build_retriever(train_dataset.corpus, base_embed_model, k=k)
bge_ndcg_test = ndcg_at_k(test_dataset, base_retriever, k)

```

%%capture base_retriever = build_retriever(train_dataset.corpus, base_embed_model, k=k) bge_ndcg_test = ndcg_at_k(test_dataset, base_retriever, k)
## Display the results¶
In [ ]:
Copied!
```
print(f"bge test - ndcg@10: {bge_ndcg_test:.2f}")
print(f"adaptor finetune test - ndcg@10: {ft_ndcg_test:.2f}")
print(f"NUDGE-N test - ndcg@10: {nudge_ndcg_test:.2f}")

```

print(f"bge test - ndcg@10: {bge_ndcg_test:.2f}") print(f"adaptor finetune test - ndcg@10: {ft_ndcg_test:.2f}") print(f"NUDGE-N test - ndcg@10: {nudge_ndcg_test:.2f}")
```
bge test - ndcg@10: 0.71
adaptor finetune test - ndcg@10: 0.72
NUDGE-N test - ndcg@10: 0.87

```

# Inserting records into the dataset¶
It's common to have your dataset expand over time. We will now insert and finetune the nfcorpus into the scifact example we've been working with. Usually you'd have to retrain on your entire dataset to avoid catastrophic forgetting. With NUDGE, you can easily expand your dataset iteratively by focusing only on the newest batch of data, without worrying about catastrophic forgetting. This only works when the new data being inserted does not conflict (e.g. new queries for old corpus or new corpus changes k-NN to old queries) with the existing dataset.
In [ ]:
Copied!
```
%%capture

new_train_dataset, new_val_dataset, new_test_dataset = load_hf_dataset(
    "nfcorpus"
)

# prepend "nfcorpus-" to the keys so they don't conflict with the scifact ids
new_train_dataset.queries = {
    f"nfcorpus-{k}": v for k, v in new_train_dataset.queries.items()
}
new_train_dataset.relevant_docs = {
    f"nfcorpus-{k}": [f"nfcorpus-{doc_id}" for doc_id in v]
    for k, v in new_train_dataset.relevant_docs.items()
}
new_train_dataset.corpus = {
    f"nfcorpus-{k}": v for k, v in new_train_dataset.corpus.items()
}

new_val_dataset.queries = {
    f"nfcorpus-{k}": v for k, v in new_val_dataset.queries.items()
}
new_val_dataset.relevant_docs = {
    f"nfcorpus-{k}": [f"nfcorpus-{doc_id}" for doc_id in v]
    for k, v in new_val_dataset.relevant_docs.items()
}
new_val_dataset.corpus = {
    f"nfcorpus-{k}": v for k, v in new_val_dataset.corpus.items()
}

new_test_dataset.queries = {
    f"nfcorpus-{k}": v for k, v in new_test_dataset.queries.items()
}
new_test_dataset.relevant_docs = {
    f"nfcorpus-{k}": [f"nfcorpus-{doc_id}" for doc_id in v]
    for k, v in new_test_dataset.relevant_docs.items()
}
new_test_dataset.corpus = {
    f"nfcorpus-{k}": v for k, v in new_test_dataset.corpus.items()
}

```

%%capture new_train_dataset, new_val_dataset, new_test_dataset = load_hf_dataset( "nfcorpus" ) # prepend "nfcorpus-" to the keys so they don't conflict with the scifact ids new_train_dataset.queries = { f"nfcorpus-{k}": v for k, v in new_train_dataset.queries.items() } new_train_dataset.relevant_docs = { f"nfcorpus-{k}": [f"nfcorpus-{doc_id}" for doc_id in v] for k, v in new_train_dataset.relevant_docs.items() } new_train_dataset.corpus = { f"nfcorpus-{k}": v for k, v in new_train_dataset.corpus.items() } new_val_dataset.queries = { f"nfcorpus-{k}": v for k, v in new_val_dataset.queries.items() } new_val_dataset.relevant_docs = { f"nfcorpus-{k}": [f"nfcorpus-{doc_id}" for doc_id in v] for k, v in new_val_dataset.relevant_docs.items() } new_val_dataset.corpus = { f"nfcorpus-{k}": v for k, v in new_val_dataset.corpus.items() } new_test_dataset.queries = { f"nfcorpus-{k}": v for k, v in new_test_dataset.queries.items() } new_test_dataset.relevant_docs = { f"nfcorpus-{k}": [f"nfcorpus-{doc_id}" for doc_id in v] for k, v in new_test_dataset.relevant_docs.items() } new_test_dataset.corpus = { f"nfcorpus-{k}": v for k, v in new_test_dataset.corpus.items() }
## Finetune the new records¶
In [ ]:
Copied!
```
%%capture

nudge.insert_data_and_finetune(
    new_train_dataset_batch=new_train_dataset,
    new_val_dataset_batch=new_val_dataset,
)
# get our corpus embeddings with the newly inserted and tuned records
nudge_corpus_embeddings = nudge.get_finetuned_corpus_embeddings()
# aggregate the corpus
aggregated_corpus = {**train_dataset.corpus, **new_train_dataset.corpus}
# build nudge retriever
nudge_retriever = build_retriever(
    aggregated_corpus, base_embed_model, nudge_corpus_embeddings, k=k
)
# get test results on nfcorpus
nudge_ndcg_nfcorpus_test = ndcg_at_k(new_test_dataset, nudge_retriever, k)
# get test results on scifact
nudge_ndcg_scifact_test = ndcg_at_k(test_dataset, nudge_retriever, k)

```

%%capture nudge.insert_data_and_finetune( new_train_dataset_batch=new_train_dataset, new_val_dataset_batch=new_val_dataset, ) # get our corpus embeddings with the newly inserted and tuned records nudge_corpus_embeddings = nudge.get_finetuned_corpus_embeddings() # aggregate the corpus aggregated_corpus = {**train_dataset.corpus, **new_train_dataset.corpus} # build nudge retriever nudge_retriever = build_retriever( aggregated_corpus, base_embed_model, nudge_corpus_embeddings, k=k ) # get test results on nfcorpus nudge_ndcg_nfcorpus_test = ndcg_at_k(new_test_dataset, nudge_retriever, k) # get test results on scifact nudge_ndcg_scifact_test = ndcg_at_k(test_dataset, nudge_retriever, k)
## Display the insertion results¶
Check the results on our newly inserted nfcorpus records and verify that our scifact benchmark did not regress.
In [ ]:
Copied!
```
print(
    f"NUDGE-N (aggregated) test on nfcorpus - ndcg@10: {nudge_ndcg_nfcorpus_test:.2f}"
)
print(
    f"NUDGE-N (aggregated) test on scifact - ndcg@10: {nudge_ndcg_scifact_test:.2f}"
)

```

print( f"NUDGE-N (aggregated) test on nfcorpus - ndcg@10: {nudge_ndcg_nfcorpus_test:.2f}" ) print( f"NUDGE-N (aggregated) test on scifact - ndcg@10: {nudge_ndcg_scifact_test:.2f}" )
```
NUDGE-N (aggregated) test on nfcorpus - ndcg@10: 0.44
NUDGE-N (aggregated) test on scifact - ndcg@10: 0.85

```

