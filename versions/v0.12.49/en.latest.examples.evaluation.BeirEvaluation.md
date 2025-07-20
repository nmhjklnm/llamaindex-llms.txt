![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# BEIR Out of Domain Benchmark¶
About BEIR:
BEIR is a heterogeneous benchmark containing diverse IR tasks. It also provides a common and easy framework for evaluation of your retrieval methods within the benchmark.
Refer to the repo via the link for a full list of supported datasets.
Here, we test the `all-MiniLM-L6-v2` sentence-transformer embedding, which is one of the fastest for the given accuracy range. We set the top_k value for the retriever to 30. We also use the nfcorpus dataset.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-huggingface

```

%pip install llama-index-embeddings-huggingface
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.evaluation.benchmarks import BeirEvaluator
from llama_index.core import VectorStoreIndex


def create_retriever(documents):
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    index = VectorStoreIndex.from_documents(
        documents, embed_model=embed_model, show_progress=True
    )
    return index.as_retriever(similarity_top_k=30)


BeirEvaluator().run(
    create_retriever, datasets=["nfcorpus"], metrics_k_values=[3, 10, 30]
)

```

from llama_index.embeddings.huggingface import HuggingFaceEmbedding from llama_index.core.evaluation.benchmarks import BeirEvaluator from llama_index.core import VectorStoreIndex def create_retriever(documents): embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5") index = VectorStoreIndex.from_documents( documents, embed_model=embed_model, show_progress=True ) return index.as_retriever(similarity_top_k=30) BeirEvaluator().run( create_retriever, datasets=["nfcorpus"], metrics_k_values=[3, 10, 30] )
```
/home/jonch/.pyenv/versions/3.10.6/lib/python3.10/site-packages/beir/datasets/data_loader.py:2: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from tqdm.autonotebook import tqdm

```

```
Dataset: nfcorpus downloaded at: /home/jonch/.cache/llama_index/datasets/BeIR__nfcorpus
Evaluating on dataset: nfcorpus
-------------------------------------

```

```
100%|███████████████████████████████████| 3633/3633 [00:00<00:00, 141316.79it/s]
Parsing documents into nodes: 100%|████████| 3633/3633 [00:06<00:00, 569.35it/s]
Generating embeddings: 100%|████████████████| 3649/3649 [04:22<00:00, 13.92it/s]

```

```
Retriever created for:  nfcorpus
Evaluating retriever on questions against qrels

```

```
100%|█████████████████████████████████████████| 323/323 [01:26<00:00,  3.74it/s]
```

```
Results for: nfcorpus
{'NDCG@3': 0.35476, 'MAP@3': 0.07489, 'Recall@3': 0.08583, 'precision@3': 0.33746}
{'NDCG@10': 0.31403, 'MAP@10': 0.11003, 'Recall@10': 0.15885, 'precision@10': 0.23994}
{'NDCG@30': 0.28636, 'MAP@30': 0.12794, 'Recall@30': 0.21653, 'precision@30': 0.14716}
-------------------------------------

```



Higher is better for all the evaluation metrics.
This towardsdatascience article covers NDCG, MAP and MRR in greater depth.
