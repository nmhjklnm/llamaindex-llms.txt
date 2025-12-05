![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Finetuning an Adapter on Top of any Black-Box Embedding Model¶
We have capabilities in LlamaIndex allowing you to fine-tune an adapter on top of embeddings produced from any model (sentence_transformers, OpenAI, and more). 
This allows you to transform your embedding representations into a new latent space that's optimized for retrieval over your specific data and queries. This can lead to small increases in retrieval performance that in turn translate to better performing RAG systems.
We do this via our `EmbeddingAdapterFinetuneEngine` abstraction. We fine-tune three types of adapters:
  * Linear
  * 2-Layer NN
  * Custom NN


## Generate Corpus¶
We use our helper abstractions, `generate_qa_embedding_pairs`, to generate our training and evaluation dataset. This function takes in any set of text nodes (chunks) and generates a structured dataset containing (question, context) pairs.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-embeddings-adapter
%pip install llama-index-finetuning

```

%pip install llama-index-embeddings-openai %pip install llama-index-embeddings-adapter %pip install llama-index-finetuning
In [ ]:
Copied!
```
import json

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import MetadataMode

```

import json from llama_index.core import SimpleDirectoryReader from llama_index.core.node_parser import SentenceSplitter from llama_index.core.schema import MetadataMode
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
In [ ]:
Copied!
```
TRAIN_FILES = ["./data/10k/lyft_2021.pdf"]
VAL_FILES = ["./data/10k/uber_2021.pdf"]

TRAIN_CORPUS_FPATH = "./data/train_corpus.json"
VAL_CORPUS_FPATH = "./data/val_corpus.json"

```

TRAIN_FILES = ["./data/10k/lyft_2021.pdf"] VAL_FILES = ["./data/10k/uber_2021.pdf"] TRAIN_CORPUS_FPATH = "./data/train_corpus.json" VAL_CORPUS_FPATH = "./data/val_corpus.json"
In [ ]:
Copied!
```
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

```

def load_corpus(files, verbose=False): if verbose: print(f"Loading files {files}") reader = SimpleDirectoryReader(input_files=files) docs = reader.load_data() if verbose: print(f"Loaded {len(docs)} docs") parser = SentenceSplitter() nodes = parser.get_nodes_from_documents(docs, show_progress=verbose) if verbose: print(f"Parsed {len(nodes)} nodes") return nodes
We do a very naive train/val split by having the Lyft corpus as the train dataset, and the Uber corpus as the val dataset.
In [ ]:
Copied!
```
train_nodes = load_corpus(TRAIN_FILES, verbose=True)
val_nodes = load_corpus(VAL_FILES, verbose=True)

```

train_nodes = load_corpus(TRAIN_FILES, verbose=True) val_nodes = load_corpus(VAL_FILES, verbose=True)
```
Loading files ['../../../examples/data/10k/lyft_2021.pdf']
Loaded 238 docs

```

```
Parsing documents into nodes:   0%|          | 0/238 [00:00<?, ?it/s]
```

```
Parsed 349 nodes
Loading files ['../../../examples/data/10k/uber_2021.pdf']
Loaded 307 docs

```

```
Parsing documents into nodes:   0%|          | 0/307 [00:00<?, ?it/s]
```

```
Parsed 418 nodes

```

### Generate synthetic queries¶
Now, we use an LLM (gpt-3.5-turbo) to generate questions using each text chunk in the corpus as context.
Each pair of (generated question, text chunk used as context) becomes a datapoint in the finetuning dataset (either for training or evaluation).
In [ ]:
Copied!
```
from llama_index.finetuning import generate_qa_embedding_pairs
from llama_index.core.evaluation import EmbeddingQAFinetuneDataset

```

from llama_index.finetuning import generate_qa_embedding_pairs from llama_index.core.evaluation import EmbeddingQAFinetuneDataset
In [ ]:
Copied!
```
train_dataset = generate_qa_embedding_pairs(train_nodes)
val_dataset = generate_qa_embedding_pairs(val_nodes)

train_dataset.save_json("train_dataset.json")
val_dataset.save_json("val_dataset.json")

```

train_dataset = generate_qa_embedding_pairs(train_nodes) val_dataset = generate_qa_embedding_pairs(val_nodes) train_dataset.save_json("train_dataset.json") val_dataset.save_json("val_dataset.json")
In [ ]:
Copied!
```
# [Optional] Load
train_dataset = EmbeddingQAFinetuneDataset.from_json("train_dataset.json")
val_dataset = EmbeddingQAFinetuneDataset.from_json("val_dataset.json")

```

# [Optional] Load train_dataset = EmbeddingQAFinetuneDataset.from_json("train_dataset.json") val_dataset = EmbeddingQAFinetuneDataset.from_json("val_dataset.json")
## Run Embedding Finetuning¶
We then fine-tune our linear adapter on top of an existing embedding model. We import our new `EmbeddingAdapterFinetuneEngine` abstraction, which takes in an existing embedding model and a set of training parameters.
#### Fine-tune bge-small-en (default)¶
In [ ]:
Copied!
```
from llama_index.finetuning import EmbeddingAdapterFinetuneEngine
from llama_index.core.embeddings import resolve_embed_model
import torch

base_embed_model = resolve_embed_model("local:BAAI/bge-small-en")

finetune_engine = EmbeddingAdapterFinetuneEngine(
    train_dataset,
    base_embed_model,
    model_output_path="model_output_test",
    # bias=True,
    epochs=4,
    verbose=True,
    # optimizer_class=torch.optim.SGD,
    # optimizer_params={"lr": 0.01}
)

```

from llama_index.finetuning import EmbeddingAdapterFinetuneEngine from llama_index.core.embeddings import resolve_embed_model import torch base_embed_model = resolve_embed_model("local:BAAI/bge-small-en") finetune_engine = EmbeddingAdapterFinetuneEngine( train_dataset, base_embed_model, model_output_path="model_output_test", # bias=True, epochs=4, verbose=True, # optimizer_class=torch.optim.SGD, # optimizer_params={"lr": 0.01} )
In [ ]:
Copied!
```
finetune_engine.finetune()

```

finetune_engine.finetune()
In [ ]:
Copied!
```
embed_model = finetune_engine.get_finetuned_model()

# alternatively import model
from llama_index.core.embeddings import LinearAdapterEmbeddingModel

# embed_model = LinearAdapterEmbeddingModel(base_embed_model, "model_output_test")

```

embed_model = finetune_engine.get_finetuned_model() # alternatively import model from llama_index.core.embeddings import LinearAdapterEmbeddingModel # embed_model = LinearAdapterEmbeddingModel(base_embed_model, "model_output_test")
## Evaluate Finetuned Model¶
We compare the fine-tuned model against the base model, as well as against text-embedding-ada-002.
We evaluate with two ranking metrics:
  * **Hit-rate metric** : For each (query, context) pair, we retrieve the top-k documents with the query. It's a hit if the results contain the ground-truth context.
  * **Mean Reciprocal Rank** : A slightly more granular ranking metric that looks at the "reciprocal rank" of the ground-truth context in the top-k retrieved set. The reciprocal rank is defined as 1/rank. Of course, if the results don't contain the context, then the reciprocal rank is 0.


In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode
from tqdm.notebook import tqdm
import pandas as pd

from eval_utils import evaluate, display_results

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import VectorStoreIndex from llama_index.core.schema import TextNode from tqdm.notebook import tqdm import pandas as pd from eval_utils import evaluate, display_results
In [ ]:
Copied!
```
ada = OpenAIEmbedding()
ada_val_results = evaluate(val_dataset, ada)

```

ada = OpenAIEmbedding() ada_val_results = evaluate(val_dataset, ada)
```
Generating embeddings:   0%|          | 0/395 [00:00<?, ?it/s]
```

```
100%|████████████████████████████████████████████████████████████████| 790/790 [03:03<00:00,  4.30it/s]

```

In [ ]:
Copied!
```
display_results(["ada"], [ada_val_results])

```

display_results(["ada"], [ada_val_results])
| retrievers | hit_rate | mrr  
---|---|---|---  
0 | ada | 0.870886 | 0.72884  
In [ ]:
Copied!
```
bge = "local:BAAI/bge-small-en"
bge_val_results = evaluate(val_dataset, bge)

```

bge = "local:BAAI/bge-small-en" bge_val_results = evaluate(val_dataset, bge)
```
Generating embeddings:   0%|          | 0/395 [00:00<?, ?it/s]
```

```
100%|████████████████████████████████████████████████████████████████| 790/790 [00:23<00:00, 33.76it/s]

```

In [ ]:
Copied!
```
display_results(["bge"], [bge_val_results])

```

display_results(["bge"], [bge_val_results])
| retrievers | hit_rate | mrr  
---|---|---|---  
0 | bge | 0.787342 | 0.643038  
In [ ]:
Copied!
```
ft_val_results = evaluate(val_dataset, embed_model)

```

ft_val_results = evaluate(val_dataset, embed_model)
```
Generating embeddings:   0%|          | 0/395 [00:00<?, ?it/s]
```

```
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 790/790 [00:21<00:00, 36.95it/s]

```

In [ ]:
Copied!
```
display_results(["ft"], [ft_val_results])

```

display_results(["ft"], [ft_val_results])
| retrievers | hit_rate | mrr  
---|---|---|---  
0 | ft | 0.798734 | 0.662152  
Here we show all the results concatenated together.
In [ ]:
Copied!
```
display_results(
    ["ada", "bge", "ft"], [ada_val_results, bge_val_results, ft_val_results]
)

```

display_results( ["ada", "bge", "ft"], [ada_val_results, bge_val_results, ft_val_results] )
| retrievers | hit_rate | mrr  
---|---|---|---  
0 | ada | 0.870886 | 0.730105  
1 | bge | 0.787342 | 0.643038  
2 | ft | 0.798734 | 0.662152  
## Fine-tune a Two-Layer Adapter¶
Let's try fine-tuning a two-layer NN as well!
It's a simple two-layer NN with a ReLU activation and a residual layer at the end.
We train for 25 epochs - longer than the linear adapter - and preserve checkpoints every 100 steps.
In [ ]:
Copied!
```
# requires torch dependency
from llama_index.core.embeddings.adapter_utils import TwoLayerNN

from llama_index.finetuning import EmbeddingAdapterFinetuneEngine
from llama_index.core.embeddings import resolve_embed_model
from llama_index.embeddings.adapter import AdapterEmbeddingModel

```

# requires torch dependency from llama_index.core.embeddings.adapter_utils import TwoLayerNN from llama_index.finetuning import EmbeddingAdapterFinetuneEngine from llama_index.core.embeddings import resolve_embed_model from llama_index.embeddings.adapter import AdapterEmbeddingModel
In [ ]:
Copied!
```
base_embed_model = resolve_embed_model("local:BAAI/bge-small-en")
adapter_model = TwoLayerNN(
    384,  # input dimension
    1024,  # hidden dimension
    384,  # output dimension
    bias=True,
    add_residual=True,
)

finetune_engine = EmbeddingAdapterFinetuneEngine(
    train_dataset,
    base_embed_model,
    model_output_path="model5_output_test",
    model_checkpoint_path="model5_ck",
    adapter_model=adapter_model,
    epochs=25,
    verbose=True,
)

```

base_embed_model = resolve_embed_model("local:BAAI/bge-small-en") adapter_model = TwoLayerNN( 384, # input dimension 1024, # hidden dimension 384, # output dimension bias=True, add_residual=True, ) finetune_engine = EmbeddingAdapterFinetuneEngine( train_dataset, base_embed_model, model_output_path="model5_output_test", model_checkpoint_path="model5_ck", adapter_model=adapter_model, epochs=25, verbose=True, )
In [ ]:
Copied!
```
finetune_engine.finetune()

```

finetune_engine.finetune()
In [ ]:
Copied!
```
embed_model_2layer = finetune_engine.get_finetuned_model(
    adapter_cls=TwoLayerNN
)

```

embed_model_2layer = finetune_engine.get_finetuned_model( adapter_cls=TwoLayerNN )
### Evaluation Results¶
Run the same evaluation script used in the previous section to measure hit-rate/MRR within the two-layer model.
In [ ]:
Copied!
```
# load model from checkpoint in the midde
embed_model_2layer = AdapterEmbeddingModel(
    base_embed_model,
    "model5_output_test",
    TwoLayerNN,
)

```

# load model from checkpoint in the midde embed_model_2layer = AdapterEmbeddingModel( base_embed_model, "model5_output_test", TwoLayerNN, )
In [ ]:
Copied!
```
from eval_utils import evaluate, display_results

```

from eval_utils import evaluate, display_results
In [ ]:
Copied!
```
ft_val_results_2layer = evaluate(val_dataset, embed_model_2layer)

```

ft_val_results_2layer = evaluate(val_dataset, embed_model_2layer)
```
Generating embeddings:   0%|          | 0/395 [00:00<?, ?it/s]
```

```
100%|████████████████████████████████████████████████████████████████| 790/790 [00:21<00:00, 36.93it/s]

```

In [ ]:
Copied!
```
# comment out if you haven't run ada/bge yet
display_results(
    ["ada", "bge", "ft_2layer"],
    [ada_val_results, bge_val_results, ft_val_results_2layer],
)

# uncomment if you just want to display the fine-tuned model's results
# display_results(["ft_2layer"], [ft_val_results_2layer])

```

# comment out if you haven't run ada/bge yet display_results( ["ada", "bge", "ft_2layer"], [ada_val_results, bge_val_results, ft_val_results_2layer], ) # uncomment if you just want to display the fine-tuned model's results # display_results(["ft_2layer"], [ft_val_results_2layer])
| retrievers | hit_rate | mrr  
---|---|---|---  
0 | ada | 0.870886 | 0.728840  
1 | bge | 0.787342 | 0.643038  
2 | ft_2layer | 0.798734 | 0.662848  
In [ ]:
Copied!
```
# load model from checkpoint in the midde
embed_model_2layer_s900 = AdapterEmbeddingModel(
    base_embed_model,
    "model5_ck/step_900",
    TwoLayerNN,
)

```

# load model from checkpoint in the midde embed_model_2layer_s900 = AdapterEmbeddingModel( base_embed_model, "model5_ck/step_900", TwoLayerNN, )
In [ ]:
Copied!
```
ft_val_results_2layer_s900 = evaluate(val_dataset, embed_model_2layer_s900)

```

ft_val_results_2layer_s900 = evaluate(val_dataset, embed_model_2layer_s900)
```
Generating embeddings:   0%|          | 0/395 [00:00<?, ?it/s]
```

```
100%|████████████████████████████████████████████████████████████████| 790/790 [00:19<00:00, 40.57it/s]

```

In [ ]:
Copied!
```
# comment out if you haven't run ada/bge yet
display_results(
    ["ada", "bge", "ft_2layer_s900"],
    [ada_val_results, bge_val_results, ft_val_results_2layer_s900],
)

# uncomment if you just want to display the fine-tuned model's results
# display_results(["ft_2layer_s900"], [ft_val_results_2layer_s900])

```

# comment out if you haven't run ada/bge yet display_results( ["ada", "bge", "ft_2layer_s900"], [ada_val_results, bge_val_results, ft_val_results_2layer_s900], ) # uncomment if you just want to display the fine-tuned model's results # display_results(["ft_2layer_s900"], [ft_val_results_2layer_s900])
| retrievers | hit_rate | mrr  
---|---|---|---  
0 | ada | 0.870886 | 0.728840  
1 | bge | 0.787342 | 0.643038  
2 | ft_2layer_s900 | 0.803797 | 0.667426  
## Try Your Own Custom Model¶
You can define your own custom adapter here! Simply subclass `BaseAdapter`, which is a light wrapper around the `nn.Module` class.
You just need to subclass `forward` and `get_config_dict`.
Just make sure you're familiar with writing `PyTorch` code :)
In [ ]:
Copied!
```
from llama_index.core.embeddings.adapter_utils import BaseAdapter
import torch.nn.functional as F
from torch import nn, Tensor
from typing import Dict

```

from llama_index.core.embeddings.adapter_utils import BaseAdapter import torch.nn.functional as F from torch import nn, Tensor from typing import Dict
In [ ]:
Copied!
```
class CustomNN(BaseAdapter):
    """Custom NN transformation.

    Is a copy of our TwoLayerNN, showing it here for notebook purposes.

    Args:
        in_features (int): Input dimension.
        hidden_features (int): Hidden dimension.
        out_features (int): Output dimension.
        bias (bool): Whether to use bias. Defaults to False.
        activation_fn_str (str): Name of activation function. Defaults to "relu".

    """

    def __init__(
        self,
        in_features: int,
        hidden_features: int,
        out_features: int,
        bias: bool = False,
        add_residual: bool = False,
    ) -> None:
        super(CustomNN, self).__init__()
        self.in_features = in_features
        self.hidden_features = hidden_features
        self.out_features = out_features
        self.bias = bias

        self.linear1 = nn.Linear(in_features, hidden_features, bias=True)
        self.linear2 = nn.Linear(hidden_features, out_features, bias=True)
        self._add_residual = add_residual
        # if add_residual, then add residual_weight (init to 0)
        self.residual_weight = nn.Parameter(torch.zeros(1))

    def forward(self, embed: Tensor) -> Tensor:
        """Forward pass (Wv).

        Args:
            embed (Tensor): Input tensor.

        """
        output1 = self.linear1(embed)
        output1 = F.relu(output1)
        output2 = self.linear2(output1)

        if self._add_residual:
            output2 = self.residual_weight * output2 + embed

        return output2

    def get_config_dict(self) -> Dict:
        """Get config dict."""
        return {
            "in_features": self.in_features,
            "hidden_features": self.hidden_features,
            "out_features": self.out_features,
            "bias": self.bias,
            "add_residual": self._add_residual,
        }

```

class CustomNN(BaseAdapter): """Custom NN transformation. Is a copy of our TwoLayerNN, showing it here for notebook purposes. Args: in_features (int): Input dimension. hidden_features (int): Hidden dimension. out_features (int): Output dimension. bias (bool): Whether to use bias. Defaults to False. activation_fn_str (str): Name of activation function. Defaults to "relu". """ def __init__( self, in_features: int, hidden_features: int, out_features: int, bias: bool = False, add_residual: bool = False, ) -> None: super(CustomNN, self).__init__() self.in_features = in_features self.hidden_features = hidden_features self.out_features = out_features self.bias = bias self.linear1 = nn.Linear(in_features, hidden_features, bias=True) self.linear2 = nn.Linear(hidden_features, out_features, bias=True) self._add_residual = add_residual # if add_residual, then add residual_weight (init to 0) self.residual_weight = nn.Parameter(torch.zeros(1)) def forward(self, embed: Tensor) -> Tensor: """Forward pass (Wv). Args: embed (Tensor): Input tensor. """ output1 = self.linear1(embed) output1 = F.relu(output1) output2 = self.linear2(output1) if self._add_residual: output2 = self.residual_weight * output2 + embed return output2 def get_config_dict(self) -> Dict: """Get config dict.""" return { "in_features": self.in_features, "hidden_features": self.hidden_features, "out_features": self.out_features, "bias": self.bias, "add_residual": self._add_residual, }
In [ ]:
Copied!
```
custom_adapter = CustomNN(
    384,  # input dimension
    1024,  # hidden dimension
    384,  # output dimension
    bias=True,
    add_residual=True,
)

finetune_engine = EmbeddingAdapterFinetuneEngine(
    train_dataset,
    base_embed_model,
    model_output_path="custom_model_output",
    model_checkpoint_path="custom_model_ck",
    adapter_model=custom_adapter,
    epochs=25,
    verbose=True,
)

```

custom_adapter = CustomNN( 384, # input dimension 1024, # hidden dimension 384, # output dimension bias=True, add_residual=True, ) finetune_engine = EmbeddingAdapterFinetuneEngine( train_dataset, base_embed_model, model_output_path="custom_model_output", model_checkpoint_path="custom_model_ck", adapter_model=custom_adapter, epochs=25, verbose=True, )
In [ ]:
Copied!
```
finetune_engine.finetune()

```

finetune_engine.finetune()
In [ ]:
Copied!
```
embed_model_custom = finetune_engine.get_finetuned_model(
    adapter_cls=CustomAdapter
)

```

embed_model_custom = finetune_engine.get_finetuned_model( adapter_cls=CustomAdapter )
### Evaluation Results¶
Run the same evaluation script used in the previous section to measure hit-rate/MRR.
In [ ]:
Copied!
```
# [optional] load model manually
# embed_model_custom = AdapterEmbeddingModel(
#     base_embed_model,
#     "custom_model_ck/step_300",
#     TwoLayerNN,
# )

```

# [optional] load model manually # embed_model_custom = AdapterEmbeddingModel( # base_embed_model, # "custom_model_ck/step_300", # TwoLayerNN, # )
In [ ]:
Copied!
```
from eval_utils import evaluate, display_results

```

from eval_utils import evaluate, display_results
In [ ]:
Copied!
```
ft_val_results_custom = evaluate(val_dataset, embed_model_custom)

```

ft_val_results_custom = evaluate(val_dataset, embed_model_custom)
```
Generating embeddings:   0%|          | 0/395 [00:00<?, ?it/s]
```

```
100%|████████████████████████████████████████████████████████████████| 790/790 [00:20<00:00, 37.77it/s]

```

In [ ]:
Copied!
```
display_results(["ft_custom"]x, [ft_val_results_custom])

```

display_results(["ft_custom"]x, [ft_val_results_custom])
| retrievers | hit_rate | mrr  
---|---|---|---  
0 | ft_custom | 0.789873 | 0.645127
