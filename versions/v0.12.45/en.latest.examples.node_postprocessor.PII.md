![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# PII Masking¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-llms-huggingface

```

%pip install llama-index-llms-openai %pip install llama-index-llms-huggingface
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core.postprocessor import (
    PIINodePostprocessor,
    NERPIINodePostprocessor,
)
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.schema import TextNode

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core.postprocessor import ( PIINodePostprocessor, NERPIINodePostprocessor, ) from llama_index.llms.huggingface import HuggingFaceLLM from llama_index.core import Document, VectorStoreIndex from llama_index.core.schema import TextNode
```
INFO:numexpr.utils:Note: NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
Note: NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
INFO:numexpr.utils:NumExpr defaulting to 8 threads.
NumExpr defaulting to 8 threads.

```

```
/home/loganm/miniconda3/envs/llama-index/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

In [ ]:
Copied!
```
# load documents
text = """
Hello Paulo Santos. The latest statement for your credit card account \
1111-0000-1111-0000 was mailed to 123 Any Street, Seattle, WA 98109.
"""
node = TextNode(text=text)

```

# load documents text = """ Hello Paulo Santos. The latest statement for your credit card account \ 1111-0000-1111-0000 was mailed to 123 Any Street, Seattle, WA 98109. """ node = TextNode(text=text)
### Option 1: Use NER Model for PII Masking¶
Use a Hugging Face NER model for PII Masking
In [ ]:
Copied!
```
processor = NERPIINodePostprocessor()

```

processor = NERPIINodePostprocessor()
In [ ]:
Copied!
```
from llama_index.core.schema import NodeWithScore

new_nodes = processor.postprocess_nodes([NodeWithScore(node=node)])

```

from llama_index.core.schema import NodeWithScore new_nodes = processor.postprocess_nodes([NodeWithScore(node=node)])
```
No model was supplied, defaulted to dbmdz/bert-large-cased-finetuned-conll03-english and revision f2482bf (https://huggingface.co/dbmdz/bert-large-cased-finetuned-conll03-english).
Using a pipeline without specifying a model name and revision in production is not recommended.
/home/loganm/miniconda3/envs/llama-index/lib/python3.11/site-packages/transformers/pipelines/token_classification.py:169: UserWarning: `grouped_entities` is deprecated and will be removed in version v5.0.0, defaulted to `aggregation_strategy="AggregationStrategy.SIMPLE"` instead.
  warnings.warn(

```

In [ ]:
Copied!
```
# view redacted text
new_nodes[0].node.get_text()

```

# view redacted text new_nodes[0].node.get_text()
Out[ ]:
```
'Hello [ORG_6]. The latest statement for your credit card account 1111-0000-1111-0000 was mailed to 123 [ORG_108] [LOC_112], [LOC_120], [LOC_129] 98109.'
```

In [ ]:
Copied!
```
# get mapping in metadata
# NOTE: this is not sent to the LLM!
new_nodes[0].node.metadata["__pii_node_info__"]

```

# get mapping in metadata # NOTE: this is not sent to the LLM! new_nodes[0].node.metadata["__pii_node_info__"]
Out[ ]:
```
{'[ORG_6]': 'Paulo Santos',
 '[ORG_108]': 'Any',
 '[LOC_112]': 'Street',
 '[LOC_120]': 'Seattle',
 '[LOC_129]': 'WA'}
```

### Option 2: Use LLM for PII Masking¶
NOTE: You should be using a _local_ LLM model for PII masking. The example shown is using OpenAI, but normally you'd use an LLM running locally, possibly from huggingface. Examples for local LLMs are here.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

processor = PIINodePostprocessor(llm=OpenAI())

```

from llama_index.llms.openai import OpenAI processor = PIINodePostprocessor(llm=OpenAI())
In [ ]:
Copied!
```
from llama_index.core.schema import NodeWithScore

new_nodes = processor.postprocess_nodes([NodeWithScore(node=node)])

```

from llama_index.core.schema import NodeWithScore new_nodes = processor.postprocess_nodes([NodeWithScore(node=node)])
In [ ]:
Copied!
```
# view redacted text
new_nodes[0].node.get_text()

```

# view redacted text new_nodes[0].node.get_text()
Out[ ]:
```
'Hello [NAME]. The latest statement for your credit card account [CREDIT_CARD_NUMBER] was mailed to [ADDRESS].'
```

In [ ]:
Copied!
```
# get mapping in metadata
# NOTE: this is not sent to the LLM!
new_nodes[0].node.metadata["__pii_node_info__"]

```

# get mapping in metadata # NOTE: this is not sent to the LLM! new_nodes[0].node.metadata["__pii_node_info__"]
Out[ ]:
```
{'NAME': 'Paulo Santos',
 'CREDIT_CARD_NUMBER': '1111-0000-1111-0000',
 'ADDRESS': '123 Any Street, Seattle, WA 98109'}
```

### Option 3: Use Presidio for PII Masking¶
Use presidio to identify and anonymize PII
In [ ]:
Copied!
```
# load documents
text = """
Hello Paulo Santos. The latest statement for your credit card account \
4095-2609-9393-4932 was mailed to Seattle, WA 98109. \
IBAN GB90YNTU67299444055881 and social security number is 474-49-7577 were verified on the system. \
Further communications will be sent to paulo@presidio.site 
"""
presidio_node = TextNode(text=text)

```

# load documents text = """ Hello Paulo Santos. The latest statement for your credit card account \ 4095-2609-9393-4932 was mailed to Seattle, WA 98109. \ IBAN GB90YNTU67299444055881 and social security number is 474-49-7577 were verified on the system. \ Further communications will be sent to paulo@presidio.site """ presidio_node = TextNode(text=text)
In [ ]:
Copied!
```
from llama_index.postprocessor.presidio import PresidioPIINodePostprocessor

processor = PresidioPIINodePostprocessor()

```

from llama_index.postprocessor.presidio import PresidioPIINodePostprocessor processor = PresidioPIINodePostprocessor()
In [ ]:
Copied!
```
from llama_index.core.schema import NodeWithScore

presidio_new_nodes = processor.postprocess_nodes(
    [NodeWithScore(node=presidio_node)]
)

```

from llama_index.core.schema import NodeWithScore presidio_new_nodes = processor.postprocess_nodes( [NodeWithScore(node=presidio_node)] )
In [ ]:
Copied!
```
# view redacted text
presidio_new_nodes[0].node.get_text()

```

# view redacted text presidio_new_nodes[0].node.get_text()
Out[ ]:
```
'\nHello <PERSON_1>. The latest statement for your credit card account <CREDIT_CARD_1> was mailed to <LOCATION_2>, <LOCATION_1>. IBAN <IBAN_CODE_1> and social security number is <US_SSN_1> were verified on the system. Further communications will be sent to <EMAIL_ADDRESS_1> \n'
```

In [ ]:
Copied!
```
# get mapping in metadata
# NOTE: this is not sent to the LLM!
presidio_new_nodes[0].node.metadata["__pii_node_info__"]

```

# get mapping in metadata # NOTE: this is not sent to the LLM! presidio_new_nodes[0].node.metadata["__pii_node_info__"]
Out[ ]:
```
{'<EMAIL_ADDRESS_1>': 'paulo@presidio.site',
 '<US_SSN_1>': '474-49-7577',
 '<IBAN_CODE_1>': 'GB90YNTU67299444055881',
 '<LOCATION_1>': 'WA 98109',
 '<LOCATION_2>': 'Seattle',
 '<CREDIT_CARD_1>': '4095-2609-9393-4932',
 '<PERSON_1>': 'Paulo Santos'}
```

### Feed Nodes to Index¶
In [ ]:
Copied!
```
# feed into index
index = VectorStoreIndex([n.node for n in new_nodes])

```

# feed into index index = VectorStoreIndex([n.node for n in new_nodes])
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 30 tokens
> [build_index_from_nodes] Total embedding token usage: 30 tokens

```

In [ ]:
Copied!
```
response = index.as_query_engine().query(
    "What address was the statement mailed to?"
)
print(str(response))

```

response = index.as_query_engine().query( "What address was the statement mailed to?" ) print(str(response))
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 8 tokens
> [retrieve] Total embedding token usage: 8 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 71 tokens
> [get_response] Total LLM token usage: 71 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

[ADDRESS]

```

